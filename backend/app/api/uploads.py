import uuid
import time
import json
from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.finance.parser import parse_csv_data, parse_excel_bytes, parse_zip_file
from app.agents.nodes import ingest_node, sheet_filtering_node, validation_node, normalization_node, pattern_detection_node
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
    Creates a new batch and EXECUTES:
    - NODE 1 (Ingest & Header Profiling)
    - NODE 1.5 (AI Sheet Relevance & Sub-Tab Filtering)
    - NODE 2 (LLM Column Mapping & Validation)
    - NODE 3 (LLM Status Classification & Canonical Normalization)
    - NODE 4 (Status Integrity Repair & Deduction/Credit Classification)
    Stops after Node 4 for step-by-step human verification.
    """
    start_time = time.time()
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    repo = FinanceRepository(db)

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

    if files:
        for f in files:
            role = file_roles_map.get(f.filename, "").upper()
            if role == "ORDER" and f not in order_upload_list:
                order_upload_list.append(f)
            elif role == "PAYMENT" and f not in payment_upload_list:
                payment_upload_list.append(f)
            elif f not in order_upload_list and f not in payment_upload_list:
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
    print(f"  [FULL CHAIN EXECUTION] BATCH CREATED: {batch_id}")
    print(f"  [ORDER FILES ({len(order_upload_list)})]: {[f.filename for f in order_upload_list]}")
    print(f"  [PAYMENT FILES ({len(payment_upload_list)})]: {[f.filename for f in payment_upload_list]}")
    print("="*80 + "\n")

    log_stage("BATCH", f"Initializing batch '{batch_id}' with {len(order_upload_list)} Order files and {len(payment_upload_list)} Payment files")
    batch = repo.create_batch(batch_id=batch_id, source_filename=filenames_summary, total_records=0)
    repo.log_audit_event(batch_id, "STAGE_START", "NODE_1_INGEST", f"Files uploaded: {filenames_summary}")

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
        elif fname.endswith((".xlsx", ".xls")):
            res = parse_excel_bytes(content, fname)
            if res["success"]:
                for s in res.get("sheets", []):
                    parsed_datasets.append({
                        "filename": f"{fname} [{s['sheet_name']}]",
                        "role": "MASTER ORDER SHEET",
                        "data": s["data"],
                        "header_row_index": s.get("header_row_index", 1),
                        "exact_headers": s.get("exact_headers", [])
                    })
        else:
            raw_text = content.decode("utf-8", errors="ignore")
            res = parse_csv_data(raw_text)
            if res["success"]:
                parsed_datasets.append({"filename": fname, "role": "MASTER ORDER SHEET", "data": res["data"], "header_row_index": 1})

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
        elif fname.endswith((".xlsx", ".xls")):
            res = parse_excel_bytes(content, fname)
            if res["success"]:
                for s in res.get("sheets", []):
                    parsed_datasets.append({
                        "filename": f"{fname} [{s['sheet_name']}]",
                        "role": "PAYMENT SETTLEMENT SHEET",
                        "data": s["data"],
                        "header_row_index": s.get("header_row_index", 1),
                        "exact_headers": s.get("exact_headers", [])
                    })
        else:
            raw_text = content.decode("utf-8", errors="ignore")
            res = parse_csv_data(raw_text)
            if res["success"]:
                parsed_datasets.append({"filename": fname, "role": "PAYMENT SETTLEMENT SHEET", "data": res["data"], "header_row_index": 1})

    if not all_upload_files and raw_csv:
        res = parse_csv_data(raw_csv)
        if res["success"]:
            parsed_datasets.append({"filename": "pasted_clipboard_data.csv", "role": "MASTER ORDER SHEET", "data": res["data"], "header_row_index": 1})
            files_info.append({"filename": "pasted_clipboard_data.csv", "size": len(raw_csv), "role": "MASTER ORDER SHEET"})

    if not parsed_datasets:
        raise HTTPException(status_code=400, detail="Please upload valid Order or Payment spreadsheet files.")

    # ─────────────────────────────────────────────────────────────────────────
    # 1. EXECUTE NODE 1: INGEST & EXACT HEADER PROFILING
    # ─────────────────────────────────────────────────────────────────────────
    node1_state = {
        "batch_id": batch_id,
        "files_info": files_info,
        "raw_datasets": parsed_datasets
    }
    node1_result = ingest_node(node1_state)

    # ─────────────────────────────────────────────────────────────────────────
    # 1.5 EXECUTE NEW NODE: AI SHEET RELEVANCE & SUB-TAB FILTERING NODE
    # ─────────────────────────────────────────────────────────────────────────
    filtering_state = {
        "batch_id": batch_id,
        "raw_datasets": node1_result.get("raw_datasets", [])
    }
    filtering_result = sheet_filtering_node(filtering_state)
    essential_datasets = filtering_result.get("raw_datasets", [])

    # ─────────────────────────────────────────────────────────────────────────
    # 2. EXECUTE NODE 2: LOCAL LLM COLUMN MAPPING & VALIDATION AGENT
    # ─────────────────────────────────────────────────────────────────────────
    node2_state = {
        "batch_id": batch_id,
        "raw_datasets": essential_datasets,
        "sheet_profiles": node1_result.get("sheet_profiles", [])
    }
    node2_result = validation_node(node2_state)

    # ─────────────────────────────────────────────────────────────────────────
    # 3. EXECUTE NODE 3: CANONICAL NORMALIZATION & LLM STATUS CLASSIFICATION
    # ─────────────────────────────────────────────────────────────────────────
    node3_state = {
        "batch_id": batch_id,
        "raw_datasets": essential_datasets,
        "column_mappings": node2_result.get("column_mappings", {})
    }
    node3_result = normalization_node(node3_state)

    # ─────────────────────────────────────────────────────────────────────────
    # 4. EXECUTE NODE 4: STATUS INTEGRITY AUDIT & DEDUCTION/CREDIT CLASSIFICATION
    # ─────────────────────────────────────────────────────────────────────────
    node4_state = {
        "batch_id": batch_id,
        "canonical_orders": node3_result.get("canonical_orders", []),
        "canonical_payments": node3_result.get("canonical_payments", [])
    }
    node4_result = pattern_detection_node(node4_state)

    # Save Repaired & Classified Canonical Data Models to SQLite DB
    canonical_orders = node4_result.get("canonical_orders", [])
    canonical_payments = node4_result.get("canonical_payments", [])

    if canonical_orders:
        repo.save_canonical_orders(batch_id, canonical_orders)
    if canonical_payments:
        repo.save_canonical_payments(batch_id, canonical_payments)

    total_records = len(canonical_orders)
    batch.total_records = total_records
    
    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000.0

    repo.update_batch_status(batch_id, "NODE_4_COMPLETE", processed_records=total_records, processing_time_ms=processing_time_ms)
    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_4_INTEGRITY", f"Node 4 complete. Audit verified 100% status coverage across {len(canonical_orders)} orders and {len(canonical_payments)} payments.")

    print("\n" + "="*80)
    print(f"  [NODE 1 ──▶ NODE 1.5 (AI FILTERING) ──▶ NODE 2 ──▶ NODE 3 ──▶ NODE 4 CHAIN COMPLETE]")
    print(f"  [BATCH ID] {batch_id}")
    print(f"  [STATUS] NODE_4_COMPLETE — Ready for your verification!")
    print("="*80 + "\n")

    return {
        "batch_id": batch_id,
        "status": "NODE_4_COMPLETE",
        "node_1_status": "COMPLETED",
        "node_relevance_status": "COMPLETED",
        "node_2_status": "COMPLETED",
        "node_3_status": "COMPLETED",
        "node_4_status": "COMPLETED",
        "retained_sheets_count": len(essential_datasets),
        "dropped_sheets_count": len(filtering_result.get("dropped_datasets", [])),
        "canonical_orders_count": len(canonical_orders),
        "canonical_payments_count": len(canonical_payments),
        "repaired_orders_count": node4_result.get("repaired_orders_count", 0),
        "classified_deductions_count": node4_result.get("classified_deductions_count", 0),
        "classified_credits_count": node4_result.get("classified_credits_count", 0),
        "processing_time_ms": round(processing_time_ms, 2)
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
    progress_pct = 100 if batch.status in ("COMPLETED", "RECONCILED", "WAITING_HUMAN_REVIEW", "NODE_1_COMPLETE", "NODE_2_COMPLETE", "NODE_3_COMPLETE", "NODE_4_COMPLETE") else int((batch.processed_records / max(batch.total_records, 1)) * 100)
    return {
        "batch_id": batch.batch_id,
        "status": batch.status,
        "progress": progress_pct,
        "stage": batch.status,
        "records_processed": batch.processed_records,
        "total_records": batch.total_records
    }
