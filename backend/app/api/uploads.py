import uuid
import time
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.finance.parser import parse_csv_data, parse_excel_bytes, parse_zip_file
from app.finance.order_normalizer import auto_map_order_columns, normalize_canonical_orders
from app.finance.payment_normalizer import auto_map_payment_columns, normalize_canonical_payments
from app.finance.reconciliation import process_reconciliation
from app.finance.exception_detector import evaluate_batch_exceptions
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.finance.metrics import calculate_batch_metrics
from app.core.logging import log_stage

router = APIRouter()

@router.post("/batches")
async def create_and_process_batch(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    raw_csv: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingests order and payment sheets, profiles columns, validates mappings,
    executes multi-source RECONCILIATION FIRST, and surfaces reconciliation exceptions
    for human review before performing profit calculations.
    """
    start_time = time.time()
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    repo = FinanceRepository(db)

    # Collect upload files
    upload_list: List[UploadFile] = []
    if files:
        upload_list.extend(files)
    if file and file not in upload_list:
        upload_list.append(file)

    filenames_summary = ", ".join([f.filename for f in upload_list]) if upload_list else "pasted_clipboard_data.csv"
    
    print("\n" + "="*80)
    print(f"  [RECONCILIATION ENGINE] NEW BATCH STARTED: {batch_id}")
    print(f"  [FILES] {filenames_summary}")
    print("="*80 + "\n")

    log_stage("BATCH", f"Initializing reconciliation batch '{batch_id}' with files: [{filenames_summary}]")
    batch = repo.create_batch(batch_id=batch_id, source_filename=filenames_summary, total_records=0)
    repo.log_audit_event(batch_id, "STAGE_START", "INGEST", f"Files uploaded: {filenames_summary}")

    all_parsed_orders = []
    all_parsed_payments = []
    all_canonical_orders = []
    all_canonical_payments = []

    # 1. DISCOVER & PARSE SHEETS
    if upload_list:
        for up_file in upload_list:
            fname = up_file.filename or "file.csv"
            content = await up_file.read()
            log_stage("PROFILER", f"Inspecting and parsing uploaded file: '{fname}'")

            if fname.endswith(".zip"):
                res = parse_zip_file(content)
                if res["success"]:
                    all_parsed_orders.extend(res["data"])
            elif fname.endswith((".xlsx", ".xls")):
                res = parse_excel_bytes(content)
                if res["success"]:
                    parsed_rows = res["data"]
                    if parsed_rows and isinstance(parsed_rows[0], dict):
                        headers_lower = [str(k).lower() for k in parsed_rows[0].keys()]
                        is_payment = any("settlement" in h or "payment" in h or "credit entry" in h for h in headers_lower)
                        if is_payment:
                            log_stage("PROFILER", f"Identified '{fname}' as PAYMENT SETTLEMENT sheet ({len(parsed_rows)} rows)")
                            all_parsed_payments.extend(parsed_rows)
                            p_map = auto_map_payment_columns(list(parsed_rows[0].keys()))
                            c_pmts = normalize_canonical_payments(__import__('pandas').DataFrame(parsed_rows), p_map, fname, "Sheet1", 2)
                            all_canonical_payments.extend(c_pmts)
                        else:
                            log_stage("PROFILER", f"Identified '{fname}' as ORDER sheet ({len(parsed_rows)} rows)")
                            all_parsed_orders.extend(parsed_rows)
                            o_map = auto_map_order_columns(list(parsed_rows[0].keys()))
                            c_ords = normalize_canonical_orders(__import__('pandas').DataFrame(parsed_rows), o_map, fname, "Sheet1", 2)
                            all_canonical_orders.extend(c_ords)
            else:
                raw_text = content.decode("utf-8", errors="ignore")
                res = parse_csv_data(raw_text)
                if res["success"]:
                    parsed_rows = res["data"]
                    if parsed_rows and isinstance(parsed_rows[0], dict):
                        headers_lower = [str(k).lower() for k in parsed_rows[0].keys()]
                        is_payment = any("settlement" in h or "payment" in h or "credit" in h for h in headers_lower)
                        if is_payment:
                            log_stage("PROFILER", f"Identified '{fname}' as PAYMENT SETTLEMENT CSV ({len(parsed_rows)} rows)")
                            all_parsed_payments.extend(parsed_rows)
                            p_map = auto_map_payment_columns(list(parsed_rows[0].keys()))
                            c_pmts = normalize_canonical_payments(__import__('pandas').DataFrame(parsed_rows), p_map, fname, "CSV", 2)
                            all_canonical_payments.extend(c_pmts)
                        else:
                            log_stage("PROFILER", f"Identified '{fname}' as ORDER CSV ({len(parsed_rows)} rows)")
                            all_parsed_orders.extend(parsed_rows)
                            o_map = auto_map_order_columns(list(parsed_rows[0].keys()))
                            c_ords = normalize_canonical_orders(__import__('pandas').DataFrame(parsed_rows), o_map, fname, "CSV", 2)
                            all_canonical_orders.extend(c_ords)

    elif raw_csv:
        res = parse_csv_data(raw_csv)
        if not res["success"]:
            repo.update_batch_status(batch_id, "FAILED")
            repo.log_audit_event(batch_id, "ERROR", "PARSING", "; ".join(res["errors"]))
            raise HTTPException(status_code=400, detail="; ".join(res["errors"]))
        all_parsed_orders = res["data"]
        if all_parsed_orders and isinstance(all_parsed_orders[0], dict):
            o_map = auto_map_order_columns(list(all_parsed_orders[0].keys()))
            all_canonical_orders = normalize_canonical_orders(__import__('pandas').DataFrame(all_parsed_orders), o_map, "pasted.csv", "Clipboard", 2)
    else:
        raise HTTPException(status_code=400, detail="Please upload spreadsheet files or paste CSV text.")

    total_records = len(all_parsed_orders)
    batch.total_records = total_records
    repo.update_batch_status(batch_id, "PROFILING", processed_records=total_records)

    # Persist Canonical Data Models
    if all_canonical_orders:
        repo.save_canonical_orders(batch_id, all_canonical_orders)
    if all_canonical_payments:
        repo.save_canonical_payments(batch_id, all_canonical_payments)

    # 2. EXECUTE RECONCILIATION FIRST (MATCHING ORDERS ↔ PAYMENTS)
    log_stage("RECONCILER", f"Matching {len(all_parsed_orders)} Orders against {len(all_parsed_payments)} Payment settlement rows...")
    repo.update_batch_status(batch_id, "RECONCILING", processed_records=total_records)

    reconciliation_res = process_reconciliation(all_parsed_orders, all_parsed_payments)
    repo.save_reconciliation_results(batch_id, reconciliation_res.get("matched", []))
    
    match_rate = reconciliation_res.get("matchRate", 0.0)
    matched_cnt = reconciliation_res.get("matchedCount", 0)
    missing_pmt_cnt = len(reconciliation_res.get("missingInPayment", []))
    missing_ord_cnt = len(reconciliation_res.get("missingInOrder", []))

    log_stage("RECONCILER", f"RECONCILIATION RESULT: {matched_cnt}/{total_records} Matched ({match_rate}% Match Rate)")
    log_stage("RECONCILER", f"DISCREPANCIES DETECTED: {missing_pmt_cnt} Missing Payments | {missing_ord_cnt} Missing Orders")

    # 3. SURFACE RECONCILIATION EXCEPTIONS FOR HUMAN GOVERNANCE FIRST
    rules = [
        {
            "pattern": r.pattern,
            "normalized_category": r.normalized_category,
            "financial_effect": r.financial_effect,
            "active": r.active
        }
        for r in repo.get_all_rules(active_only=True)
    ]
    exceptions = evaluate_batch_exceptions(all_parsed_orders, reconciliation_res, rules)

    # Check SKU Cost Price Availability (Defer P&L calculation until user configures/approves)
    sku_costs_map = repo.get_sku_costs_map()
    grouped = group_by_sku(all_parsed_orders)

    for sku_id in grouped.keys():
        unit_cost = sku_costs_map.get(sku_id, 0.0)
        if unit_cost <= 0:
            exceptions.append({
                "record_id": f"cost-{sku_id}",
                "order_id": "N/A",
                "exception_type": "MISSING_COST_PRICE",
                "raw_status": f"SKU {sku_id}",
                "amount": 0.0,
                "description": f"SKU '{sku_id}' is missing unit cost price. Please configure unit cost.",
                "confidence": 1.0,
                "status": "PENDING",
                "requires_human": True
            })

    repo.save_exceptions(batch_id, exceptions)

    # Defer Profit Calculation: Initial P&L computed using current database costs
    profit_res = calculate_overall_profit(grouped, sku_costs_map)

    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000.0

    metrics = calculate_batch_metrics(batch_id, total_records, reconciliation_res, exceptions, profit_res, processing_time_ms)
    repo.save_report(batch_id, "PROFIT_AND_RECONCILIATION", metrics, profit_res.get("overall", {}), profit_res.get("skuBreakdowns", {}))

    pending_human = any(e.get("requires_human", False) and e.get("status") == "PENDING" for e in exceptions)
    final_status = "WAITING_HUMAN_REVIEW" if pending_human else "RECONCILED"
    repo.update_batch_status(batch_id, final_status, processed_records=total_records, processing_time_ms=processing_time_ms)

    print("\n" + "="*80)
    print(f"  [RECONCILIATION SUMMARY] Batch {batch_id} Processing Complete!")
    print(f"  [MATCH RATE] {match_rate}% | Matched: {matched_cnt} | Missing Pmt: {missing_pmt_cnt}")
    print(f"  [EXCEPTIONS SURFACED] {len(exceptions)} requiring human review/approval")
    print("="*80 + "\n")

    return {
        "batch_id": batch_id,
        "status": final_status,
        "total_records": total_records,
        "match_rate": metrics["match_rate"],
        "total_profit": metrics["total_profit"],
        "unresolved_exceptions": len(exceptions),
        "processing_time_ms": round(processing_time_ms, 2),
        "throughput_records_per_sec": metrics["throughput_records_per_sec"]
    }


@router.get("/batches/{batch_id}")
def get_batch_details(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    batch = repo.get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    report = repo.get_latest_report(batch_id)
    return {
        "batch_id": batch.batch_id,
        "status": batch.status,
        "source_filename": batch.source_filename,
        "total_records": batch.total_records,
        "processed_records": batch.processed_records,
        "processing_time_ms": batch.processing_time_ms,
        "created_at": batch.created_at,
        "summary": report.summary_json if report else {}
    }


@router.get("/batches/{batch_id}/progress")
def get_batch_progress(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    batch = repo.get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    progress_pct = 100 if batch.status in ("COMPLETED", "RECONCILED", "WAITING_HUMAN_REVIEW") else int((batch.processed_records / max(batch.total_records, 1)) * 100)
    return {
        "batch_id": batch.batch_id,
        "status": batch.status,
        "progress": progress_pct,
        "stage": batch.status,
        "records_processed": batch.processed_records,
        "total_records": batch.total_records
    }
