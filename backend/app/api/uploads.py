import uuid
import time
from typing import Optional, List, Dict, Any, Tuple
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

def classify_and_separate_datasets(parsed_datasets: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Classifies parsed datasets into Order datasets vs Payment Settlement datasets
    based on filename and column header keywords.
    """
    orders_list = []
    payments_list = []

    for item in parsed_datasets:
        fname = item.get("filename", "").lower()
        rows = item.get("data", [])
        if not rows or not isinstance(rows[0], dict):
            continue

        headers_lower = [str(k).lower() for k in rows[0].keys()]
        
        # Check payment indicators
        is_payment_file = "payment" in fname or "settlement" in fname or "payout" in fname
        is_payment_header = any("final settlement amount" in h or "reason for credit entry" in h or "payment status" in h or "settlement" in h for h in headers_lower)

        if is_payment_file or is_payment_header:
            log_stage("PROFILER", f"Classified dataset '{item.get('filename')}' as PAYMENT SETTLEMENT ({len(rows)} rows)")
            payments_list.extend(rows)
        else:
            log_stage("PROFILER", f"Classified dataset '{item.get('filename')}' as MASTER ORDER SHEET ({len(rows)} rows)")
            orders_list.extend(rows)

    return orders_list, payments_list


@router.post("/batches")
async def create_and_process_batch(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    raw_csv: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new batch supporting multiple file uploads (order sheets + settlement payment sheets),
    profiles spreadsheet columns, converts into CanonicalOrder and CanonicalPayment models,
    executes multi-event reconciliation, profit calculations, and exception detection.
    """
    start_time = time.time()
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    repo = FinanceRepository(db)

    # Collect all uploaded files
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

    parsed_datasets: List[Dict[str, Any]] = []

    if upload_list:
        for up_file in upload_list:
            fname = up_file.filename or "file.csv"
            content = await up_file.read()
            log_stage("PROFILER", f"Inspecting uploaded file: '{fname}'")

            if fname.endswith(".zip"):
                zip_res = parse_zip_file(content)
                if zip_res["success"]:
                    for f_entry in zip_res.get("files", []):
                        parsed_datasets.append({
                            "filename": f_entry["filename"],
                            "data": f_entry["data"]
                        })
            elif fname.endswith((".xlsx", ".xls")):
                res = parse_excel_bytes(content, fname)
                if res["success"]:
                    parsed_datasets.append({
                        "filename": fname,
                        "data": res["data"]
                    })
            else:
                raw_text = content.decode("utf-8", errors="ignore")
                res = parse_csv_data(raw_text)
                if res["success"]:
                    parsed_datasets.append({
                        "filename": fname,
                        "data": res["data"]
                    })
    elif raw_csv:
        res = parse_csv_data(raw_csv)
        if res["success"]:
            parsed_datasets.append({
                "filename": "pasted_clipboard_data.csv",
                "data": res["data"]
            })
    else:
        raise HTTPException(status_code=400, detail="Please upload spreadsheet files or paste CSV text.")

    # Classify Datasets into Master Order Sheet vs Payment Settlement Sheets
    all_parsed_orders, all_parsed_payments = classify_and_separate_datasets(parsed_datasets)

    log_stage("PROFILER", f"Final Separation: {len(all_parsed_orders)} Master Order rows | {len(all_parsed_payments)} Payment Settlement rows")

    # Canonical Normalization & Database Persistence
    all_canonical_orders = []
    all_canonical_payments = []

    if all_parsed_orders and isinstance(all_parsed_orders[0], dict):
        o_map = auto_map_order_columns(list(all_parsed_orders[0].keys()))
        all_canonical_orders = normalize_canonical_orders(__import__('pandas').DataFrame(all_parsed_orders), o_map, filenames_summary, "OrderSheet", 2)
        repo.save_canonical_orders(batch_id, all_canonical_orders)

    if all_parsed_payments and isinstance(all_parsed_payments[0], dict):
        p_map = auto_map_payment_columns(list(all_parsed_payments[0].keys()))
        all_canonical_payments = normalize_canonical_payments(__import__('pandas').DataFrame(all_parsed_payments), p_map, filenames_summary, "PaymentSheet", 2)
        repo.save_canonical_payments(batch_id, all_canonical_payments)

    total_records = len(all_parsed_orders)
    batch.total_records = total_records
    repo.update_batch_status(batch_id, "RECONCILING", processed_records=total_records)

    # 1. RECONCILIATION MATCHING MASTER ORDERS ↔ PAYMENT SETTLEMENTS
    log_stage("RECONCILER", f"Matching {total_records} Master Orders against {len(all_parsed_payments)} Payment settlement rows...")
    reconciliation_res = process_reconciliation(all_parsed_orders, all_parsed_payments)
    repo.save_reconciliation_results(batch_id, reconciliation_res.get("matched", []))
    
    match_rate = reconciliation_res.get("matchRate", 0.0)
    matched_cnt = reconciliation_res.get("matchedCount", 0)
    missing_pmt_cnt = len(reconciliation_res.get("missingInPayment", []))
    missing_ord_cnt = len(reconciliation_res.get("missingInOrder", []))

    log_stage("RECONCILER", f"RECONCILIATION RESULT: {matched_cnt}/{total_records} Matched ({match_rate}% Match Rate)")
    log_stage("RECONCILER", f"DISCREPANCIES DETECTED: {missing_pmt_cnt} Missing Payments | {missing_ord_cnt} Historical Payment Rows")

    # 2. SURFACE HIGH-LEVEL CONCISE GOVERNANCE EXCEPTIONS (NO 1,900 ROW CARD SPAM)
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

    # 3. GROUP MISSING SKU COST PRICES INTO 1 SUMMARY GOVERNANCE CARD (NEVER 1,900 CARDS!)
    sku_costs_map = repo.get_sku_costs_map()
    grouped = group_by_sku(all_parsed_orders)
    missing_cost_skus = [sku_id for sku_id in grouped.keys() if sku_costs_map.get(sku_id, 0.0) <= 0]

    if missing_cost_skus:
        cnt_skus = len(missing_cost_skus)
        sample_skus = ", ".join(missing_cost_skus[:5])
        exceptions.append({
            "record_id": "summary-missing-sku-costs",
            "order_id": f"{cnt_skus} SKUs Missing Unit Costs (Samples: {sample_skus})",
            "exception_type": "MISSING_COST_PRICE",
            "raw_status": "SKU Unit Cost Missing",
            "amount": 0.0,
            "description": f"{cnt_skus} unique SKUs in this batch require cost price configuration for accurate P&L calculation.",
            "confidence": 1.0,
            "status": "PENDING",
            "requires_human": True,
            "occurrences": cnt_skus
        })

    repo.save_exceptions(batch_id, exceptions)

    # Profit Calculation
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
    print(f"  [MATCH RATE] {match_rate}% | Matched: {matched_cnt} / {total_records}")
    print(f"  [EXCEPTIONS SURFACED] {len(exceptions)} concise governance summary cards requiring review")
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
