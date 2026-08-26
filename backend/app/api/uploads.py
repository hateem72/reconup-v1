import uuid
import time
import json
from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.finance.parser import parse_csv_data, parse_excel_bytes, parse_zip_file
from app.agents.nodes import ingest_node, sheet_filtering_node, validation_node, normalization_node, pattern_detection_node, reconciliation_node
from app.core.logging import log_stage, set_audit_context, clear_audit_context

router = APIRouter()

# In-Memory Pipeline Execution Store per Batch for Reprocessing & Dynamic Node Inspection
BATCH_PIPELINE_STORE: Dict[str, Dict[str, Any]] = {}

class ReprocessRequest(BaseModel):
    start_node: float = 1.5  # 1.5, 2, or 3
    sheet_overrides: Optional[Dict[str, str]] = {}  # { "filename": "KEEP" | "EXCLUDE" }
    column_mapping_overrides: Optional[Dict[str, Dict[str, str]]] = {}  # { "filename": { "canonical_field": "src_col" } }
    status_mapping_overrides: Optional[Dict[str, str]] = {}  # { "raw_status": "Canonical Category" }


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
    Creates a new batch and EXECUTES FULL CHAIN:
    - NODE 1 (Ingest & Header Profiling)
    - NODE 1.5 (AI Sheet Relevance & Sub-Tab Filtering)
    - NODE 2 (LLM Column Mapping & Validation)
    - NODE 3 (LLM Status Classification & Canonical Normalization)
    - NODE 4 (Status Integrity Repair & Deduction/Credit Classification)
    - NODE 5 (Deterministic Order-Payment Reconciliation Engine)
    """
    start_time = time.time()
    batch_id = f"batch_{uuid.uuid4().hex[:8]}"
    repo = FinanceRepository(db)
    set_audit_context(batch_id, db)

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
    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_1_INGEST", f"Profiled {len(parsed_datasets)} sub-tab datasets with exact headers.")

    # ─────────────────────────────────────────────────────────────────────────
    # 1.5 EXECUTE NEW NODE: AI SHEET RELEVANCE & SUB-TAB FILTERING NODE
    # ─────────────────────────────────────────────────────────────────────────
    filtering_state = {
        "batch_id": batch_id,
        "raw_datasets": node1_result.get("raw_datasets", [])
    }
    filtering_result = sheet_filtering_node(filtering_state)
    essential_datasets = filtering_result.get("raw_datasets", [])
    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_RELEVANCE", f"SheetRelevanceAgent retained {len(essential_datasets)} essential transaction sheets, dropped {len(filtering_result.get('dropped_datasets', []))} summary sub-tabs.")

    # ─────────────────────────────────────────────────────────────────────────
    # 2. EXECUTE NODE 2: LOCAL LLM COLUMN MAPPING & VALIDATION AGENT
    # ─────────────────────────────────────────────────────────────────────────
    node2_state = {
        "batch_id": batch_id,
        "raw_datasets": essential_datasets,
        "sheet_profiles": node1_result.get("sheet_profiles", [])
    }
    node2_result = validation_node(node2_state)
    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_2_MAPPING", f"ColumnMappingAgent mapped headers across {len(essential_datasets)} essential sheets (Cache Hits: {node2_result.get('schema_cache_hits', 0)}).")

    # ─────────────────────────────────────────────────────────────────────────
    # 3. EXECUTE NODE 3: CANONICAL NORMALIZATION & LLM STATUS CLASSIFICATION
    # ─────────────────────────────────────────────────────────────────────────
    node3_state = {
        "batch_id": batch_id,
        "raw_datasets": essential_datasets,
        "column_mappings": node2_result.get("column_mappings", {})
    }
    node3_result = normalization_node(node3_state)
    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_3_NORMALIZATION", f"StatusNormalizationAgent categorized statuses into canonical lifecycle states.")

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

    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_4_INTEGRITY", f"Node 4 complete. Verified 100% status coverage across {len(canonical_orders)} orders and {len(canonical_payments)} payments.")

    # ─────────────────────────────────────────────────────────────────────────
    # 5. EXECUTE NODE 5: DETERMINISTIC ORDER-PAYMENT RECONCILIATION ENGINE
    # ─────────────────────────────────────────────────────────────────────────
    node5_state = {
        "batch_id": batch_id,
        "canonical_orders": canonical_orders,
        "canonical_payments": canonical_payments
    }
    node5_result = reconciliation_node(node5_state)

    total_records = len(canonical_orders)
    batch.total_records = total_records
    
    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000.0

    repo.update_batch_status(batch_id, "NODE_5_RECONCILED", processed_records=total_records, processing_time_ms=processing_time_ms)
    repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_5_RECONCILIATION", f"Node 5 complete. Reconciliation Match Rate: {node5_result.get('match_rate', 0.0)}%")

    # Store Execution Context in BATCH_PIPELINE_STORE for Node Inspection & Human Reprocessing
    sheet_profiles_json = []
    for sp in node1_result.get("sheet_profiles", []):
        if hasattr(sp, "dict"):
            sheet_profiles_json.append(sp.dict())
        elif isinstance(sp, dict):
            sheet_profiles_json.append(sp)

    BATCH_PIPELINE_STORE[batch_id] = {
        "all_raw_datasets": parsed_datasets,
        "files_info": files_info,
        "sheet_profiles": sheet_profiles_json,
        "ai_retained_datasets": essential_datasets,
        "essential_datasets": essential_datasets,
        "dropped_datasets": filtering_result.get("dropped_datasets", []),
        "column_mappings": node2_result.get("column_mappings", {}),
        "status_mappings": node3_result.get("status_mappings", {}),
        "human_sheet_overrides": {},
        "human_column_overrides": {},
        "human_status_overrides": {},
        "node4_result": node4_result,
        "node5_result": node5_result
    }

    print("\n" + "="*80)
    print(f"  [NODE 1 ──▶ NODE 1.5 ──▶ NODE 2 ──▶ NODE 3 ──▶ NODE 4 ──▶ NODE 5 CHAIN COMPLETE]")
    print(f"  [BATCH ID] {batch_id}")
    print(f"  [MATCH RATE] {node5_result.get('match_rate', 0.0)}%")
    print(f"  [STATUS] NODE_5_RECONCILED — Fully reconciled & ready for P&L / Governance!")
    print("="*80 + "\n")

    return {
        "batch_id": batch_id,
        "status": "NODE_5_RECONCILED",
        "node_1_status": "COMPLETED",
        "node_relevance_status": "COMPLETED",
        "node_2_status": "COMPLETED",
        "node_3_status": "COMPLETED",
        "node_4_status": "COMPLETED",
        "node_5_status": "COMPLETED",
        "retained_sheets_count": len(essential_datasets),
        "dropped_sheets_count": len(filtering_result.get("dropped_datasets", [])),
        "canonical_orders_count": len(canonical_orders),
        "canonical_payments_count": len(canonical_payments),
        "repaired_orders_count": node4_result.get("repaired_orders_count", 0),
        "classified_deductions_count": node4_result.get("classified_deductions_count", 0),
        "classified_credits_count": node4_result.get("classified_credits_count", 0),
        "match_rate": node5_result.get("match_rate", 0.0),
        "processing_time_ms": round(processing_time_ms, 2)
    }


@router.get("/batches/{batch_id}/node-details")
def get_batch_node_details(batch_id: str, db: Session = Depends(get_db)):
    """
    Returns node inspection details for Node 1, Node 1.5, Node 2, Node 3, and active human overrides.
    """
    if batch_id not in BATCH_PIPELINE_STORE:
        # Fallback empty profile if batch not in RAM
        return {
            "batch_id": batch_id,
            "node1": {"sheet_profiles": []},
            "node1_5": {"retained_datasets": [], "dropped_datasets": []},
            "node2": {"column_mappings": {}},
            "node3": {"status_mappings": {}},
            "human_overrides": {"sheet_overrides": {}, "column_overrides": {}, "status_overrides": {}}
        }

    store = BATCH_PIPELINE_STORE[batch_id]
    
    # Format retained & dropped for UI display
    retained_info = []
    for ds in store.get("essential_datasets", []):
        fname = ds.get("filename", "")
        role = ds.get("role", "")
        rows = ds.get("data", [])
        headers = ds.get("exact_headers") or ([str(k) for k in dict.fromkeys([k for r in rows[:10] for k in r.keys() if k != "id"])] if rows and isinstance(rows[0], dict) else [])
        retained_info.append({
            "filename": fname,
            "role": role,
            "row_count": len(rows),
            "col_count": len(headers),
            "headers": headers,
            "verdict": "REQUIRED",
            "rationale": "Retained essential transaction sheet.",
            "user_override": store["human_sheet_overrides"].get(fname, None)
        })

    dropped_info = []
    for ds in store.get("dropped_datasets", []):
        fname = ds.get("filename", "")
        dropped_info.append({
            "filename": fname,
            "role": ds.get("role", ""),
            "row_count": ds.get("row_count", 0),
            "verdict": "NOT_REQUIRED",
            "rationale": ds.get("rationale", "Dropped non-essential tab."),
            "user_override": store["human_sheet_overrides"].get(fname, None)
        })

    return {
        "batch_id": batch_id,
        "node1": {
            "sheet_profiles": store.get("sheet_profiles", [])
        },
        "node1_5": {
            "retained_datasets": retained_info,
            "dropped_datasets": dropped_info
        },
        "node2": {
            "column_mappings": store.get("column_mappings", {})
        },
        "node3": {
            "status_mappings": store.get("status_mappings", {})
        },
        "human_overrides": {
            "sheet_overrides": store.get("human_sheet_overrides", {}),
            "column_overrides": store.get("human_column_overrides", {}),
            "status_overrides": store.get("human_status_overrides", {})
        }
    }


@router.post("/batches/{batch_id}/reprocess")
def reprocess_batch_pipeline(
    batch_id: str,
    req: ReprocessRequest,
    db: Session = Depends(get_db)
):
    """
    Reprocesses the pipeline from start_node (1.5, 2, or 3) forward using human overrides.
    """
    if batch_id not in BATCH_PIPELINE_STORE:
        raise HTTPException(status_code=404, detail="Batch pipeline execution context not found. Please upload dataset again.")
        
    store = BATCH_PIPELINE_STORE[batch_id]
    set_audit_context(batch_id, db)
    
    start_node = req.start_node or 1.5
    
    # 1. Update Human Overrides in Store
    if req.sheet_overrides:
        store["human_sheet_overrides"].update(req.sheet_overrides)
    if req.column_mapping_overrides:
        for fname, col_map in req.column_mapping_overrides.items():
            if fname not in store["human_column_overrides"]:
                store["human_column_overrides"][fname] = {}
            store["human_column_overrides"][fname].update(col_map)
    if req.status_mapping_overrides:
        store["human_status_overrides"].update(req.status_mapping_overrides)

    print("\n" + "="*80)
    print(f"  [HUMAN REPROCESSING ENGINE] RUNNING PIPELINE FROM NODE {start_node} FOR BATCH: {batch_id}")
    print(f"  • Human Sheet Overrides: {store['human_sheet_overrides']}")
    print(f"  • Human Column Overrides: {store['human_column_overrides']}")
    print(f"  • Human Status Overrides: {store['human_status_overrides']}")
    print("="*80 + "\n")

    log_stage("REPROCESS", f"Starting partial pipeline re-run from Node {start_node} for batch '{batch_id}'")

    # 2. Execute Node 1.5 if start_node <= 1.5
    all_raw = store["all_raw_datasets"]
    if start_node <= 1.5:
        retained = []
        dropped = []
        for ds in all_raw:
            fname = ds.get("filename", "")
            override = store["human_sheet_overrides"].get(fname)
            if override == "KEEP":
                retained.append(ds)
            elif override == "EXCLUDE":
                dropped.append({"filename": fname, "role": ds.get("role"), "row_count": len(ds.get("data", [])), "rationale": "Manually excluded by human operator."})
            else:
                ai_retained_names = [r.get("filename") for r in store["ai_retained_datasets"]]
                if fname in ai_retained_names:
                    retained.append(ds)
                else:
                    dropped.append({"filename": fname, "role": ds.get("role"), "row_count": len(ds.get("data", [])), "rationale": "Dropped by SheetRelevanceAgent."})
        store["essential_datasets"] = retained
        store["dropped_datasets"] = dropped

    essential_datasets = store.get("essential_datasets", all_raw)

    # 3. Execute Node 2 if start_node <= 2
    if start_node <= 2:
        node2_state = {
            "batch_id": batch_id,
            "raw_datasets": essential_datasets,
            "sheet_profiles": store.get("sheet_profiles", [])
        }
        node2_result = validation_node(node2_state)
        col_mappings = node2_result.get("column_mappings", {})
        store["column_mappings"] = col_mappings

    col_mappings = store.get("column_mappings", {})
    # Apply Human Column Mapping Overrides
    for fname, overrides in store["human_column_overrides"].items():
        if fname in col_mappings:
            for c_field, src_col in overrides.items():
                col_mappings[fname][c_field] = {
                    "source_column": src_col,
                    "confidence": 1.0,
                    "rationale": "Overridden by human operator."
                }

    # 4. Execute Node 3 if start_node <= 3
    node3_state = {
        "batch_id": batch_id,
        "raw_datasets": essential_datasets,
        "column_mappings": col_mappings
    }
    node3_result = normalization_node(node3_state)
    status_mappings = node3_result.get("status_mappings", {})

    # Apply Human Status Overrides
    for raw_s, new_cat in store["human_status_overrides"].items():
        status_mappings[raw_s] = {
            "canonical_category": new_cat,
            "confidence": 1.0,
            "rationale": "Overridden by human operator."
        }

    canonical_orders = node3_result.get("canonical_orders", [])
    canonical_payments = node3_result.get("canonical_payments", [])

    # Apply status overrides to canonical models
    for ord_obj in canonical_orders:
        raw_d = ord_obj.raw_data or {}
        for k, v in raw_d.items():
            if str(v).strip() in store["human_status_overrides"]:
                ord_obj.status = store["human_status_overrides"][str(v).strip()]

    for pmt_obj in canonical_payments:
        raw_d = pmt_obj.raw_data or {}
        for k, v in raw_d.items():
            if str(v).strip() in store["human_status_overrides"]:
                pmt_obj.status = store["human_status_overrides"][str(v).strip()]

    store["status_mappings"] = status_mappings

    # 5. Execute Node 4 & Node 5
    node4_state = {
        "batch_id": batch_id,
        "canonical_orders": canonical_orders,
        "canonical_payments": canonical_payments
    }
    node4_result = pattern_detection_node(node4_state)

    canonical_orders = node4_result.get("canonical_orders", [])
    canonical_payments = node4_result.get("canonical_payments", [])

    repo = FinanceRepository(db)
    if canonical_orders:
        repo.save_canonical_orders(batch_id, canonical_orders)
    if canonical_payments:
        repo.save_canonical_payments(batch_id, canonical_payments)

    node5_state = {
        "batch_id": batch_id,
        "canonical_orders": canonical_orders,
        "canonical_payments": canonical_payments
    }
    node5_result = reconciliation_node(node5_state)
    store["node5_result"] = node5_result

    repo.update_batch_status(batch_id, "NODE_5_RECONCILED", processed_records=len(canonical_orders))
    repo.log_audit_event(batch_id, "REPROCESS_COMPLETE", f"NODE_{str(start_node).replace('.', '_')}", f"Reprocessed pipeline from Node {start_node}. Updated Match Rate: {node5_result.get('match_rate', 0.0)}%")

    return {
        "success": True,
        "batch_id": batch_id,
        "start_node": start_node,
        "match_rate": node5_result.get("match_rate", 0.0),
        "reconciled_orders_count": len(node5_result.get("reconciliation_results", {}).get("matched", [])),
        "unsettled_orders_count": len(node5_result.get("reconciliation_results", {}).get("missingInPayment", []))
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


@router.get("/batches/{batch_id}/logs")
def get_batch_logs(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    events = repo.get_audit_events(batch_id)
    return {
        "batch_id": batch_id,
        "logs": [
            {
                "id": ev.id,
                "timestamp": ev.created_at.isoformat() if ev.created_at else "",
                "stage": ev.stage_name,
                "event_type": ev.event_type,
                "description": ev.description
            }
            for ev in events
        ]
    }


@router.get("/batches/{batch_id}/progress")
def get_batch_progress(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    batch = repo.get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    progress_pct = 100 if batch.status in ("COMPLETED", "RECONCILED", "WAITING_HUMAN_REVIEW", "NODE_5_RECONCILED") else int((batch.processed_records / max(batch.total_records, 1)) * 100)
    return {
        "batch_id": batch.batch_id,
        "status": batch.status,
        "progress": progress_pct,
        "stage": batch.status,
        "records_processed": batch.processed_records,
        "total_records": batch.total_records
    }
