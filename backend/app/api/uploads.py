import uuid
import time
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.finance.parser import parse_csv_data, parse_excel_bytes, parse_zip_file
from app.finance.validator import validate_sales_data
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.finance.reconciliation import process_reconciliation
from app.finance.exception_detector import evaluate_batch_exceptions, detect_unknown_patterns
from app.finance.metrics import calculate_batch_metrics

router = APIRouter()

@router.post("/batches")
async def create_and_process_batch(
    file: Optional[UploadFile] = File(None),
    raw_csv: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new batch, parses spreadsheet files, runs reconciliation, profit calculations,
    and exception detection asynchronously or inline.
    """
    start_time = time.time()
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    repo = FinanceRepository(db)

    filename = file.filename if file else "pasted_clipboard_data.csv"
    batch = repo.create_batch(batch_id=batch_id, source_filename=filename, total_records=0)

    parsed_orders = []
    parsed_payments = []
    errors = []

    if file:
        content = await file.read()
        if filename.endswith(".zip"):
            res = parse_zip_file(content)
        elif filename.endswith((".xlsx", ".xls")):
            res = parse_excel_bytes(content)
        else:
            raw_text = content.decode("utf-8", errors="ignore")
            res = parse_csv_data(raw_text)

        if not res["success"]:
            repo.update_batch_status(batch_id, "FAILED")
            raise HTTPException(status_code=400, detail="; ".join(res["errors"]))
        parsed_orders = res["data"]
    elif raw_csv:
        res = parse_csv_data(raw_csv)
        if not res["success"]:
            repo.update_batch_status(batch_id, "FAILED")
            raise HTTPException(status_code=400, detail="; ".join(res["errors"]))
        parsed_orders = res["data"]
    else:
        raise HTTPException(status_code=400, detail="Please upload an Excel/CSV file or paste CSV text.")

    total_records = len(parsed_orders)
    batch.total_records = total_records
    repo.update_batch_status(batch_id, "RECONCILING", processed_records=total_records)

    # 1. Reconciliation
    reconciliation_res = process_reconciliation(parsed_orders, parsed_payments)
    repo.save_reconciliation_results(batch_id, reconciliation_res.get("matched", []))

    # 2. Profit Calculation
    grouped = group_by_sku(parsed_orders)
    profit_res = calculate_overall_profit(grouped)

    # 3. Exceptions & Rules
    rules = [
        {
            "pattern": r.pattern,
            "normalized_category": r.normalized_category,
            "financial_effect": r.financial_effect,
            "active": r.active
        }
        for r in repo.get_all_rules(active_only=True)
    ]
    exceptions = evaluate_batch_exceptions(parsed_orders, reconciliation_res, rules)
    repo.save_exceptions(batch_id, exceptions)

    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000.0

    # 4. Metrics & Report
    metrics = calculate_batch_metrics(batch_id, total_records, reconciliation_res, exceptions, profit_res, processing_time_ms)
    repo.save_report(batch_id, "PROFIT_AND_RECONCILIATION", metrics, profit_res.get("overall", {}), profit_res.get("skuBreakdowns", {}))

    pending_human = any(e.get("requires_human", False) and e.get("status") == "PENDING" for e in exceptions)
    final_status = "WAITING_HUMAN_REVIEW" if pending_human else "COMPLETED"
    repo.update_batch_status(batch_id, final_status, processed_records=total_records, processing_time_ms=processing_time_ms)

    return {
        "batch_id": batch_id,
        "status": final_status,
        "total_records": total_records,
        "match_rate": metrics["match_rate"],
        "total_profit": metrics["total_profit"],
        "unresolved_exceptions": metrics["unresolved_exceptions"],
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
    progress_pct = 100 if batch.status in ("COMPLETED", "WAITING_HUMAN_REVIEW") else int((batch.processed_records / max(batch.total_records, 1)) * 100)
    return {
        "batch_id": batch.batch_id,
        "status": batch.status,
        "progress": progress_pct,
        "stage": batch.status,
        "records_processed": batch.processed_records,
        "total_records": batch.total_records
    }
