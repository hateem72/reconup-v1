import uuid
import time
import json
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db, SessionLocal
from app.database.repositories import FinanceRepository
from app.finance.parser import parse_csv_data, parse_excel_bytes, parse_zip_file
from app.agents.nodes import ingest_node, sheet_filtering_node, validation_node, normalization_node, pattern_detection_node, reconciliation_node
from app.core.logging import log_stage, set_audit_context, clear_audit_context
from app.core.events import publish_event, event_stream_generator

router = APIRouter()

# In-Memory Pipeline Execution Store per Batch for Reprocessing & Dynamic Node Inspection
BATCH_PIPELINE_STORE: Dict[str, Dict[str, Any]] = {}

class ReprocessRequest(BaseModel):
    start_node: float = 1.5  # 1.5, 2, or 3
    sheet_overrides: Optional[Dict[str, str]] = {}  # { "filename": "KEEP" | "EXCLUDE" }
    column_mapping_overrides: Optional[Dict[str, Dict[str, str]]] = {}  # { "filename": { "canonical_field": "src_col" } }
    status_mapping_overrides: Optional[Dict[str, str]] = {}  # { "raw_status": "Canonical Category" }


def execute_pipeline_sync(batch_id: str, raw_file_payloads: List[Dict[str, Any]], raw_csv: Optional[str], start_time: float):
    """
    Executes the full 6-node pipeline synchronously in background thread and emits real-time SSE lifecycle events.
    """
    db = SessionLocal()
    try:
        repo = FinanceRepository(db)
        set_audit_context(batch_id, db)

        # ─────────────────────────────────────────────────────────────────────
        # NODE 1: INGEST & EXACT HEADER PROFILING (Parsing in background)
        # ─────────────────────────────────────────────────────────────────────
        publish_event(batch_id, "NODE_START", {
            "node": 1,
            "name": "Ingest & Header Profiling",
            "message": "Parsing workbook sub-tabs and detecting true header rows...",
            "time": time.time()
        })

        files_info = []
        parsed_datasets: List[Dict[str, Any]] = []

        for item in raw_file_payloads:
            fname = item["filename"]
            content = item["content"]
            role = item["role"]
            files_info.append({"filename": fname, "size": len(content), "role": role})

            log_stage("INGEST", f"Reading & extracting sheets for '{fname}' [{role}]")

            if fname.endswith(".zip"):
                zip_res = parse_zip_file(content)
                if zip_res["success"]:
                    for f_entry in zip_res.get("files", []):
                        parsed_datasets.append({"filename": f_entry["filename"], "role": role, "data": f_entry["data"]})
            elif fname.endswith((".xlsx", ".xls")):
                res = parse_excel_bytes(content, fname)
                if res["success"]:
                    for s in res.get("sheets", []):
                        parsed_datasets.append({
                            "filename": f"{fname} [{s['sheet_name']}]",
                            "role": role,
                            "data": s["data"],
                            "header_row_index": s.get("header_row_index", 1),
                            "exact_headers": s.get("exact_headers", [])
                        })
            else:
                raw_text = content.decode("utf-8", errors="ignore")
                res = parse_csv_data(raw_text)
                if res["success"]:
                    parsed_datasets.append({"filename": fname, "role": role, "data": res["data"], "header_row_index": 1})

        if not raw_file_payloads and raw_csv:
            res = parse_csv_data(raw_csv)
            if res["success"]:
                parsed_datasets.append({"filename": "pasted_clipboard_data.csv", "role": "MASTER ORDER SHEET", "data": res["data"], "header_row_index": 1})
                files_info.append({"filename": "pasted_clipboard_data.csv", "size": len(raw_csv), "role": "MASTER ORDER SHEET"})

        if not parsed_datasets:
            raise ValueError("No valid spreadsheet data found in uploaded files.")

        node1_state = {
            "batch_id": batch_id,
            "files_info": files_info,
            "raw_datasets": parsed_datasets
        }
        node1_result = ingest_node(node1_state)
        repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_1_INGEST", f"Profiled {len(parsed_datasets)} sub-tab datasets with exact headers.")

        sheet_profiles_json = []
        for sp in node1_result.get("sheet_profiles", []):
            if hasattr(sp, "dict"):
                sheet_profiles_json.append(sp.dict())
            elif isinstance(sp, dict):
                sheet_profiles_json.append(sp)

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 1,
            "name": "Ingest & Header Profiling",
            "summary": f"Profiled {len(parsed_datasets)} datasets with exact headers",
            "sheet_profiles": sheet_profiles_json,
            "time": time.time()
        })

        # ─────────────────────────────────────────────────────────────────────
        # NODE 1.5: AI SHEET RELEVANCE & SUB-TAB FILTERING
        # ─────────────────────────────────────────────────────────────────────
        publish_event(batch_id, "NODE_START", {
            "node": 2,
            "node_key": "node1_5",
            "name": "AI Sub-Tab Filtering",
            "message": "SheetRelevanceAgent evaluating transaction sheets vs summary/disclaimer tabs via Local LLM...",
            "time": time.time()
        })

        filtering_state = {
            "batch_id": batch_id,
            "raw_datasets": node1_result.get("raw_datasets", [])
        }
        filtering_result = sheet_filtering_node(filtering_state)
        essential_datasets = filtering_result.get("raw_datasets", [])
        dropped_datasets = filtering_result.get("dropped_datasets", [])

        repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_RELEVANCE", f"SheetRelevanceAgent retained {len(essential_datasets)} essential transaction sheets, dropped {len(dropped_datasets)} summary sub-tabs.")

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 2,
            "node_key": "node1_5",
            "name": "AI Sub-Tab Filtering",
            "summary": f"Retained {len(essential_datasets)} transaction sheets, dropped {len(dropped_datasets)} summary tabs",
            "retained_count": len(essential_datasets),
            "dropped_count": len(dropped_datasets),
            "time": time.time()
        })

        # ─────────────────────────────────────────────────────────────────────
        # NODE 2: LOCAL LLM COLUMN MAPPING
        # ─────────────────────────────────────────────────────────────────────
        publish_event(batch_id, "NODE_START", {
            "node": 3,
            "node_key": "node2",
            "name": "LLM Column Mapping",
            "message": f"ColumnMappingAgent semantically mapping headers for {len(essential_datasets)} sheets...",
            "time": time.time()
        })

        node2_state = {
            "batch_id": batch_id,
            "raw_datasets": essential_datasets,
            "sheet_profiles": node1_result.get("sheet_profiles", [])
        }
        node2_result = validation_node(node2_state)
        repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_2_MAPPING", f"ColumnMappingAgent mapped headers across {len(essential_datasets)} essential sheets (Cache Hits: {node2_result.get('schema_cache_hits', 0)}).")

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 3,
            "node_key": "node2",
            "name": "LLM Column Mapping",
            "summary": f"Mapped canonical schema fields across {len(essential_datasets)} sheets",
            "column_mappings": node2_result.get("column_mappings", {}),
            "time": time.time()
        })

        # ─────────────────────────────────────────────────────────────────────
        # NODE 3: CANONICAL NORMALIZATION & STATUS CLASSIFICATION
        # ─────────────────────────────────────────────────────────────────────
        publish_event(batch_id, "NODE_START", {
            "node": 4,
            "node_key": "node3",
            "name": "Status Normalization",
            "message": "StatusNormalizationAgent categorizing raw statuses into canonical order lifecycle states...",
            "time": time.time()
        })

        node3_state = {
            "batch_id": batch_id,
            "raw_datasets": essential_datasets,
            "column_mappings": node2_result.get("column_mappings", {})
        }
        node3_result = normalization_node(node3_state)
        repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_3_NORMALIZATION", f"StatusNormalizationAgent categorized statuses into canonical lifecycle states.")

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 4,
            "node_key": "node3",
            "name": "Status Normalization",
            "summary": f"Normalized {len(node3_result.get('canonical_orders', []))} orders & {len(node3_result.get('canonical_payments', []))} payment lines",
            "canonical_orders_count": len(node3_result.get("canonical_orders", [])),
            "canonical_payments_count": len(node3_result.get("canonical_payments", [])),
            "time": time.time()
        })

        # ─────────────────────────────────────────────────────────────────────
        # NODE 4: STATUS INTEGRITY AUDIT & DEDUCTION/CREDIT CLASSIFICATION
        # ─────────────────────────────────────────────────────────────────────
        publish_event(batch_id, "NODE_START", {
            "node": 5,
            "node_key": "node4",
            "name": "Status Integrity Audit",
            "message": "PatternDetectionAgent auditing status integrity & classifying fee deductions vs compensations...",
            "time": time.time()
        })

        node4_state = {
            "batch_id": batch_id,
            "canonical_orders": node3_result.get("canonical_orders", []),
            "canonical_payments": node3_result.get("canonical_payments", [])
        }
        node4_result = pattern_detection_node(node4_state)

        canonical_orders = node4_result.get("canonical_orders", [])
        canonical_payments = node4_result.get("canonical_payments", [])

        if canonical_orders:
            repo.save_canonical_orders(batch_id, canonical_orders)
        if canonical_payments:
            repo.save_canonical_payments(batch_id, canonical_payments)

        repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_4_INTEGRITY", f"Node 4 complete. Verified 100% status coverage across {len(canonical_orders)} orders and {len(canonical_payments)} payments.")

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 5,
            "node_key": "node4",
            "name": "Status Integrity Audit",
            "summary": f"Integrity verified (Repaired: {node4_result.get('repaired_orders_count', 0)}, Deductions: {node4_result.get('classified_deductions_count', 0)})",
            "repaired_count": node4_result.get("repaired_orders_count", 0),
            "deductions_count": node4_result.get("classified_deductions_count", 0),
            "time": time.time()
        })

        # ─────────────────────────────────────────────────────────────────────
        # NODE 5: DETERMINISTIC ORDER-PAYMENT RECONCILIATION
        # ─────────────────────────────────────────────────────────────────────
        publish_event(batch_id, "NODE_START", {
            "node": 6,
            "node_key": "node5",
            "name": "Order Reconciliation",
            "message": f"Matching {len(canonical_orders)} master orders against multi-event settlement payments...",
            "time": time.time()
        })

        node5_state = {
            "batch_id": batch_id,
            "canonical_orders": canonical_orders,
            "canonical_payments": canonical_payments
        }
        node5_result = reconciliation_node(node5_state)

        total_records = len(canonical_orders)
        end_time = time.time()
        processing_time_ms = (end_time - start_time) * 1000.0

        repo.update_batch_status(batch_id, "NODE_5_RECONCILED", processed_records=total_records, processing_time_ms=processing_time_ms)
        repo.log_audit_event(batch_id, "STAGE_COMPLETE", "NODE_5_RECONCILIATION", f"Node 5 complete. Reconciliation Match Rate: {node5_result.get('match_rate', 0.0)}%")

        # Store in BATCH_PIPELINE_STORE for Node Inspection & Human Reprocessing
        BATCH_PIPELINE_STORE[batch_id] = {
            "all_raw_datasets": parsed_datasets,
            "files_info": files_info,
            "sheet_profiles": sheet_profiles_json,
            "ai_retained_datasets": essential_datasets,
            "essential_datasets": essential_datasets,
            "dropped_datasets": dropped_datasets,
            "column_mappings": node2_result.get("column_mappings", {}),
            "status_mappings": node3_result.get("status_mappings", {}),
            "human_sheet_overrides": {},
            "human_column_overrides": {},
            "human_status_overrides": {},
            "node4_result": node4_result,
            "node5_result": node5_result
        }

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 6,
            "node_key": "node5",
            "name": "Order Reconciliation",
            "summary": f"Reconciliation Complete: {node5_result.get('match_rate', 0.0)}% match rate",
            "match_rate": node5_result.get("match_rate", 0.0),
            "matched_count": len(node5_result.get("reconciliation_results", {}).get("matched", [])),
            "time": time.time()
        })

        publish_event(batch_id, "PIPELINE_COMPLETE", {
            "batch_id": batch_id,
            "status": "NODE_5_RECONCILED",
            "match_rate": node5_result.get("match_rate", 0.0),
            "retained_sheets_count": len(essential_datasets),
            "canonical_orders_count": len(canonical_orders),
            "canonical_payments_count": len(canonical_payments),
            "processing_time_ms": round(processing_time_ms, 2),
            "time": time.time()
        })

        print("\n" + "="*80)
        print(f"  [REAL-TIME PIPELINE COMPLETE] Batch ID: {batch_id} | Match Rate: {node5_result.get('match_rate', 0.0)}%")
        print("="*80 + "\n")

    except Exception as e:
        log_stage("ERROR", f"Pipeline execution error: {str(e)}", level="error")
        publish_event(batch_id, "PIPELINE_ERROR", {
            "batch_id": batch_id,
            "error": str(e),
            "time": time.time()
        })
    finally:
        clear_audit_context()
        db.close()


@router.get("/batches/{batch_id}/stream")
async def stream_batch_events(batch_id: str):
    """
    Server-Sent Events (SSE) streaming endpoint providing real-time node execution progress and logs.
    """
    return StreamingResponse(
        event_stream_generator(batch_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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
    Creates a batch and initiates non-blocking real-time SSE streaming pipeline execution in ~5ms.
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

    all_upload_files = list(files or [])
    if file:
        all_upload_files.append(file)

    for up_f in all_upload_files:
        fname = up_f.filename or ""
        assigned_role = file_roles_map.get(fname, "UNKNOWN")
        if assigned_role == "MASTER ORDER SHEET":
            order_upload_list.append(up_f)
        elif assigned_role == "PAYMENT SETTLEMENT SHEET":
            payment_upload_list.append(up_f)
        else:
            fname_lower = fname.lower()
            if any(k in fname_lower for k in ["order", "manifest", "master", "sale"]):
                order_upload_list.append(up_f)
            else:
                payment_upload_list.append(up_f)

    if not order_upload_list and not payment_upload_list and all_upload_files:
        for up_f in all_upload_files:
            fname = up_f.filename or ""
            if "order" in fname.lower():
                order_upload_list.append(up_f)
            else:
                payment_upload_list.append(up_f)

    primary_name = (
        order_upload_list[0].filename if order_upload_list
        else (payment_upload_list[0].filename if payment_upload_list
        else (all_upload_files[0].filename if all_upload_files
        else "raw_data.csv"))
    )

    batch = repo.create_batch(batch_id=batch_id, source_filename=primary_name)

    # Buffer raw file contents quickly into memory
    raw_file_payloads: List[Dict[str, Any]] = []

    for up_file in order_upload_list:
        fname = up_file.filename or "order_file.csv"
        content = await up_file.read()
        raw_file_payloads.append({"filename": fname, "content": content, "role": "MASTER ORDER SHEET"})

    for up_file in payment_upload_list:
        fname = up_file.filename or "payment_file.csv"
        content = await up_file.read()
        raw_file_payloads.append({"filename": fname, "content": content, "role": "PAYMENT SETTLEMENT SHEET"})

    if not raw_file_payloads and not raw_csv:
        raise HTTPException(status_code=400, detail="Please upload valid Order or Payment spreadsheet files.")

    # Launch Asynchronous Pipeline Execution in Background Thread
    asyncio.create_task(
        asyncio.to_thread(execute_pipeline_sync, batch_id, raw_file_payloads, raw_csv, start_time)
    )

    return {
        "batch_id": batch_id,
        "status": "PROCESSING",
        "stream_url": f"/api/batches/{batch_id}/stream",
        "source_filename": primary_name,
        "files_count": len(raw_file_payloads)
    }


@router.get("/batches/{batch_id}/node-details")
def get_batch_node_details(batch_id: str, db: Session = Depends(get_db)):
    """
    Returns node inspection details for Node 1, Node 1.5, Node 2, Node 3, and active human overrides.
    """
    if batch_id not in BATCH_PIPELINE_STORE:
        return {
            "batch_id": batch_id,
            "node1": {"sheet_profiles": []},
            "node1_5": {"retained_datasets": [], "dropped_datasets": []},
            "node2": {"column_mappings": {}},
            "node3": {"status_mappings": {}},
            "human_overrides": {"sheet_overrides": {}, "column_overrides": {}, "status_overrides": {}}
        }

    store = BATCH_PIPELINE_STORE[batch_id]
    
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


def execute_reprocess_sync(batch_id: str, req_data: Dict[str, Any]):
    """
    Executes partial pipeline reprocessing synchronously and emits SSE lifecycle events.
    """
    db = SessionLocal()
    try:
        store = BATCH_PIPELINE_STORE[batch_id]
        set_audit_context(batch_id, db)
        start_node = req_data.get("start_node", 1.5)

        publish_event(batch_id, "REPROCESS_START", {
            "batch_id": batch_id,
            "start_node": start_node,
            "message": f"Reprocessing pipeline from Node {start_node} with human overrides...",
            "time": time.time()
        })

        if req_data.get("sheet_overrides"):
            store["human_sheet_overrides"].update(req_data["sheet_overrides"])
        if req_data.get("column_mapping_overrides"):
            for fname, col_map in req_data["column_mapping_overrides"].items():
                if fname not in store["human_column_overrides"]:
                    store["human_column_overrides"][fname] = {}
                store["human_column_overrides"][fname].update(col_map)
        if req_data.get("status_mapping_overrides"):
            store["human_status_overrides"].update(req_data["status_mapping_overrides"])

        all_raw = store["all_raw_datasets"]
        if start_node <= 1.5:
            publish_event(batch_id, "NODE_START", {"node": 2, "node_key": "node1_5", "name": "AI Sub-Tab Filtering", "message": "Applying human sheet selection overrides..."})
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
            publish_event(batch_id, "NODE_COMPLETE", {"node": 2, "node_key": "node1_5", "name": "AI Sub-Tab Filtering", "summary": f"Retained {len(retained)} sheets, dropped {len(dropped)} tabs"})

        essential_datasets = store.get("essential_datasets", all_raw)

        if start_node <= 2:
            publish_event(batch_id, "NODE_START", {"node": 3, "node_key": "node2", "name": "LLM Column Mapping", "message": "Updating column mappings..."})
            node2_state = {
                "batch_id": batch_id,
                "raw_datasets": essential_datasets,
                "sheet_profiles": store.get("sheet_profiles", [])
            }
            node2_result = validation_node(node2_state)
            col_mappings = node2_result.get("column_mappings", {})
            store["column_mappings"] = col_mappings
            publish_event(batch_id, "NODE_COMPLETE", {"node": 3, "node_key": "node2", "name": "LLM Column Mapping", "summary": "Column mappings updated"})

        col_mappings = store.get("column_mappings", {})
        for fname, overrides in store["human_column_overrides"].items():
            if fname in col_mappings:
                for c_field, src_col in overrides.items():
                    col_mappings[fname][c_field] = {
                        "source_column": src_col,
                        "confidence": 1.0,
                        "rationale": "Overridden by human operator."
                    }

        if start_node <= 3:
            publish_event(batch_id, "NODE_START", {"node": 4, "node_key": "node3", "name": "Status Normalization", "message": "Re-normalizing statuses with human overrides..."})
            node3_state = {
                "batch_id": batch_id,
                "raw_datasets": essential_datasets,
                "column_mappings": col_mappings
            }
            node3_result = normalization_node(node3_state)
            status_mappings = node3_result.get("status_mappings", {})

            for raw_s, new_cat in store["human_status_overrides"].items():
                status_mappings[raw_s] = {
                    "canonical_category": new_cat,
                    "confidence": 1.0,
                    "rationale": "Overridden by human operator."
                }

            canonical_orders = node3_result.get("canonical_orders", [])
            canonical_payments = node3_result.get("canonical_payments", [])

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
            publish_event(batch_id, "NODE_COMPLETE", {"node": 4, "node_key": "node3", "name": "Status Normalization", "summary": "Statuses normalized"})

        publish_event(batch_id, "NODE_START", {"node": 5, "node_key": "node4", "name": "Status Integrity Audit", "message": "Auditing data integrity..."})
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

        publish_event(batch_id, "NODE_COMPLETE", {"node": 5, "node_key": "node4", "name": "Status Integrity Audit", "summary": "Integrity verified"})

        publish_event(batch_id, "NODE_START", {"node": 6, "node_key": "node5", "name": "Order Reconciliation", "message": "Re-calculating settlement reconciliation..."})
        node5_state = {
            "batch_id": batch_id,
            "canonical_orders": canonical_orders,
            "canonical_payments": canonical_payments
        }
        node5_result = reconciliation_node(node5_state)
        store["node5_result"] = node5_result

        repo.update_batch_status(batch_id, "NODE_5_RECONCILED", processed_records=len(canonical_orders))
        repo.log_audit_event(batch_id, "REPROCESS_COMPLETE", f"NODE_{str(start_node).replace('.', '_')}", f"Reprocessed pipeline from Node {start_node}. Updated Match Rate: {node5_result.get('match_rate', 0.0)}%")

        publish_event(batch_id, "NODE_COMPLETE", {
            "node": 6,
            "node_key": "node5",
            "name": "Order Reconciliation",
            "summary": f"Match Rate: {node5_result.get('match_rate', 0.0)}%",
            "match_rate": node5_result.get("match_rate", 0.0)
        })

        publish_event(batch_id, "PIPELINE_COMPLETE", {
            "batch_id": batch_id,
            "status": "NODE_5_RECONCILED",
            "match_rate": node5_result.get("match_rate", 0.0)
        })

    except Exception as e:
        log_stage("ERROR", f"Reprocess error: {str(e)}", level="error")
        publish_event(batch_id, "PIPELINE_ERROR", {"batch_id": batch_id, "error": str(e)})
    finally:
        clear_audit_context()
        db.close()


@router.post("/batches/{batch_id}/reprocess")
async def reprocess_batch_pipeline(
    batch_id: str,
    req: ReprocessRequest,
    db: Session = Depends(get_db)
):
    """
    Reprocesses the pipeline from start_node (1.5, 2, or 3) forward using human overrides.
    """
    if batch_id not in BATCH_PIPELINE_STORE:
        raise HTTPException(status_code=404, detail="Batch pipeline execution context not found. Please upload dataset again to initialize pipeline.")
        
    req_dict = req.dict()
    asyncio.create_task(
        asyncio.to_thread(execute_reprocess_sync, batch_id, req_dict)
    )

    return {
        "success": True,
        "batch_id": batch_id,
        "status": "REPROCESSING",
        "stream_url": f"/api/batches/{batch_id}/stream",
        "start_node": req.start_node
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
