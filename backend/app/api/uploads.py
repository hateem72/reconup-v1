import uuid
import time
import json
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
from app.agents.nodes import ingest_node
from app.core.logging import log_stage

router = APIRouter()

@router.post("/batches")
async def create_and_process_batch(
    order_files: Optional[List[UploadFile]] = File(None),
    payment_files: Optional[List[UploadFile]] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    raw_csv: Optional[str] = Form(None),
    file_roles_json: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new batch supporting explicit designation of Order Sheets vs Payment Settlement Sheets.
    Executes NODE 1 (Ingest & Profiling) outputting clear file role designations in the terminal console.
    """
    start_time = time.time()
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    repo = FinanceRepository(db)

    # Parse role map if sent as JSON string
    file_roles_map = {}
    if file_roles_json:
        try:
            file_roles_map = json.loads(file_roles_json)
        except Exception:
            pass

    order_upload_list: List[UploadFile] = []
    payment_upload_list: List[UploadFile] = []

    if order_files:
        order_upload_list.extend(order_files)
    if payment_files:
        payment_upload_list.extend(payment_files)

    # Handle legacy/fallback files parameter
    if files:
        for f in files:
            role = file_roles_map.get(f.filename, "").upper()
            if role == "ORDER" and f not in order_upload_list:
                order_upload_list.append(f)
            elif role == "PAYMENT" and f not in payment_upload_list:
                payment_upload_list.append(f)
            elif f not in order_upload_list and f not in payment_upload_list:
                # Default heuristic based on filename
                if "payment" in f.filename.lower() or "settlement" in f.filename.lower() or "payout" in f.filename.lower():
                    payment_upload_list.append(f)
                else:
                    order_upload_list.append(f)

    if file:
        role = file_roles_map.get(file.filename, "").upper()
        if role == "PAYMENT":
            if file not in payment_upload_list: payment_upload_list.append(file)
        else:
            if file not in order_upload_list: order_upload_list.append(file)

    all_upload_files = order_upload_list + payment_upload_list
    filenames_summary = ", ".join([f.filename for f in all_upload_files]) if all_upload_files else "pasted_clipboard_data.csv"
    
    print("\n" + "="*80)
    print(f"  [RECONCILIATION ENGINE] NEW BATCH STARTED: {batch_id}")
    print(f"  [ORDER FILES ({len(order_upload_list)})]: {[f.filename for f in order_upload_list]}")
    print(f"  [PAYMENT FILES ({len(payment_upload_list)})]: {[f.filename for f in payment_upload_list]}")
    print("="*80 + "\n")

    log_stage("BATCH", f"Initializing batch '{batch_id}' with {len(order_upload_list)} Order files and {len(payment_upload_list)} Payment files")
    batch = repo.create_batch(batch_id=batch_id, source_filename=filenames_summary, total_records=0)
    repo.log_audit_event(batch_id, "STAGE_START", "NODE_1_INGEST", f"Files uploaded: {filenames_summary}")

    all_parsed_orders = []
    all_parsed_payments = []
    parsed_datasets = []
    files_info = []

    # 1. PROCESS EXPLICIT ORDER FILES
    for up_file in order_upload_list:
        fname = up_file.filename or "order_file.csv"
        content = await up_file.read()
        files_info.append({"filename": fname, "size": len(content), "role": "MASTER ORDER SHEET"})

        if fname.endswith(".zip"):
            zip_res = parse_zip_file(content)
            if zip_res["success"]:
                for f_entry in zip_res.get("files", []):
                    parsed_datasets.append({"filename": f_entry["filename"], "role": "MASTER ORDER SHEET", "data": f_entry["data"]})
                    all_parsed_orders.extend(f_entry["data"])
        elif fname.endswith((".xlsx", ".xls")):
            res = parse_excel_bytes(content, fname)
            if res["success"]:
                parsed_datasets.append({"filename": fname, "role": "MASTER ORDER SHEET", "data": res["data"]})
                all_parsed_orders.extend(res["data"])
        else:
            raw_text = content.decode("utf-8", errors="ignore")
            res = parse_csv_data(raw_text)
            if res["success"]:
                parsed_datasets.append({"filename": fname, "role": "MASTER ORDER SHEET", "data": res["data"]})
                all_parsed_orders.extend(res["data"])

    # 2. PROCESS EXPLICIT PAYMENT FILES
    for up_file in payment_upload_list:
        fname = up_file.filename or "payment_file.csv"
        content = await up_file.read()
        files_info.append({"filename": fname, "size": len(content), "role": "PAYMENT SETTLEMENT SHEET"})

        if fname.endswith(".zip"):
            zip_res = parse_zip_file(content)
            if zip_res["success"]:
                for f_entry in zip_res.get("files", []):
                    parsed_datasets.append({"filename": f_entry["filename"], "role": "PAYMENT SETTLEMENT SHEET", "data": f_entry["data"]})
                    all_parsed_payments.extend(f_entry["data"])
        elif fname.endswith((".xlsx", ".xls")):
            res = parse_excel_bytes(content, fname)
            if res["success"]:
                parsed_datasets.append({"filename": fname, "role": "PAYMENT SETTLEMENT SHEET", "data": res["data"]})
                all_parsed_payments.extend(res["data"])
        else:
            raw_text = content.decode("utf-8", errors="ignore")
            res = parse_csv_data(raw_text)
            if res["success"]:
                parsed_datasets.append({"filename": fname, "role": "PAYMENT SETTLEMENT SHEET", "data": res["data"]})
                all_parsed_payments.extend(res["data"])

    # Fallback to pasted CSV
    if not all_upload_files and raw_csv:
        res = parse_csv_data(raw_csv)
        if res["success"]:
            parsed_datasets.append({"filename": "pasted_clipboard_data.csv", "role": "MASTER ORDER SHEET", "data": res["data"]})
            all_parsed_orders.extend(res["data"])
            files_info.append({"filename": "pasted_clipboard_data.csv", "size": len(raw_csv), "role": "MASTER ORDER SHEET"})

    if not all_parsed_orders and not all_parsed_payments:
        raise HTTPException(status_code=400, detail="Please upload valid Order or Payment spreadsheet files.")

    # ─────────────────────────────────────────────────────────────────────────
    # RUN NODE 1: INGEST & SHEET PROFILING (CONSOLE VERIFICATION)
    # ─────────────────────────────────────────────────────────────────────────
    node1_state = {
        "batch_id": batch_id,
        "files_info": files_info,
        "raw_datasets": parsed_datasets
    }
    node1_result = ingest_node(node1_state)

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
    repo.update_batch_status(batch_id, "PROFILING_NODE_1_COMPLETE", processed_records=total_records)

    # 1. RECONCILIATION MATCHING
    log_stage("RECONCILER", f"Matching {total_records} Master Orders against {len(all_parsed_payments)} Payment settlement rows...")
    reconciliation_res = process_reconciliation(all_parsed_orders, all_parsed_payments)
    repo.save_reconciliation_results(batch_id, reconciliation_res.get("matched", []))
    
    match_rate = reconciliation_res.get("matchRate", 0.0)
    matched_cnt = reconciliation_res.get("matchedCount", 0)

    # 2. GOVERNANCE EXCEPTIONS
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

    # SKU Cost Summary Exception Card
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
            "description": f"{cnt_skus} unique SKUs in this batch require cost price configuration.",
            "confidence": 1.0,
            "status": "PENDING",
            "requires_human": True,
            "occurrences": cnt_skus
        })

    repo.save_exceptions(batch_id, exceptions)

    profit_res = calculate_overall_profit(grouped, sku_costs_map)
    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000.0

    metrics = calculate_batch_metrics(batch_id, total_records, reconciliation_res, exceptions, profit_res, processing_time_ms)
    repo.save_report(batch_id, "PROFIT_AND_RECONCILIATION", metrics, profit_res.get("overall", {}), profit_res.get("skuBreakdowns", {}))

    pending_human = any(e.get("requires_human", False) and e.get("status") == "PENDING" for e in exceptions)
    final_status = "WAITING_HUMAN_REVIEW" if pending_human else "RECONCILED"
    repo.update_batch_status(batch_id, final_status, processed_records=total_records, processing_time_ms=processing_time_ms)

    return {
        "batch_id": batch_id,
        "status": final_status,
        "node_1_status": "COMPLETED",
        "order_files_count": len(order_upload_list),
        "payment_files_count": len(payment_upload_list),
        "total_orders": total_records,
        "total_payments": len(all_parsed_payments),
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
