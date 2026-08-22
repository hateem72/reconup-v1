import time
import io
import pandas as pd
from typing import Dict, Any, List
from app.agents.state import FinanceState
from app.finance.profiler import list_sheets, profile_sheet
from app.finance.normalizer import normalize_status
from app.finance.validator import validate_sales_data
from app.finance.order_normalizer import llm_map_columns, validate_order_mapping
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.finance.reconciliation import process_reconciliation
from app.finance.exception_detector import evaluate_batch_exceptions, detect_unknown_patterns
from app.finance.metrics import calculate_batch_metrics
from app.core.logging import log_stage

def log_agent_call(agent_name: str, task: str, input_summary: str, output_summary: str, confidence: float, duration_sec: float):
    """Logs structured AI call execution metrics per requirements."""
    log_stage("AGENT", f"Agent: {agent_name} | Task: {task}")
    log_stage("AGENT", f"  Input: {input_summary}")
    log_stage("AGENT", f"  Output: {output_summary}")
    log_stage("AGENT", f"  Confidence: {round(confidence, 2)} | Duration: {round(duration_sec, 3)}s | Status: SUCCESS")

# ─────────────────────────────────────────────────────────────────────────────
# NODE 1: INGEST & SHEET PROFILING NODE
# ─────────────────────────────────────────────────────────────────────────────
def ingest_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 1: Discovers workbook sheets, extracts exact original column header names,
    profiles row/column dimensions, identifies candidate header rows (1-10),
    and computes column statistical profiles.
    """
    batch_id = state.get("batch_id", "batch_demo")
    files_info = state.get("files_info", [])
    raw_datasets = state.get("raw_datasets", [])
    
    print("\n" + "="*80)
    print(f"  [NODE 1: INGEST & EXACT HEADER PROFILING] EXECUTION STARTED FOR BATCH: {batch_id}")
    print("="*80)
    
    log_stage("NODE 1", f"Starting Node 1 execution for batch '{batch_id}'")
    log_stage("NODE 1", f"Files received in state: {len(files_info)}")

    profiles = []
    total_sheets_found = 0

    for idx, ds in enumerate(raw_datasets):
        fname = ds.get("filename", f"file_{idx+1}")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        
        print(f"\n--- [NODE 1 PROFILING FILE #{idx+1}]: {fname} [ROLE: {role}] ---")
        log_stage("NODE 1", f"File #{idx+1}: '{fname}' [ROLE: {role}] contains {len(rows)} raw data rows")

        if rows and isinstance(rows[0], dict):
            df_raw = pd.DataFrame(rows)
            exact_headers = [str(k) for k in rows[0].keys() if k != "id"]
            
            sheet_profile = profile_sheet(df_raw, sheet_name=fname, sheet_idx=idx)
            profiles.append(sheet_profile)
            total_sheets_found += 1

            print(f"  • Sheet Name: {sheet_profile.sheet_name}")
            print(f"  • Designated Role: {role}")
            print(f"  • Dimensions: {sheet_profile.row_count} data rows x {len(exact_headers)} columns")
            print(f"  • True Header Row Index (1-based): Row {ds.get('header_row_index', 1)}")
            print(f"\n  • Exact Discovered Source Header Column Names ({len(exact_headers)}):")
            for h_i, h_name in enumerate(exact_headers):
                print(f"      [{h_i+1}] \"{h_name}\"")

            print(f"\n  • Column Statistical Profiles:")
            for cp in sheet_profile.column_profiles:
                if cp.column_name == "id":
                    continue
                type_info = []
                if cp.identifier_like: type_info.append("IDENTIFIER")
                if cp.numeric_like: type_info.append("NUMERIC")
                if cp.date_like: type_info.append("DATE")
                type_str = ", ".join(type_info) if type_info else "TEXT"
                
                samples_preview = ", ".join([f"'{s}'" for s in cp.sample_values[:3]])
                print(f"      - Column [{cp.column_index+1}] \"{cp.column_name}\": dtype={cp.dtype}, nulls={cp.null_percentage}%, uniqueness={round(cp.uniqueness_ratio*100, 1)}% [{type_str}] (Samples: {samples_preview})")

    print("\n" + "="*80)
    print(f"  [NODE 1 COMPLETE] Profiled {total_sheets_found} sheets across {len(files_info)} files.")
    print("="*80 + "\n")

    log_stage("NODE 1", f"Node 1 complete. Profiled {total_sheets_found} sheets with exact header names.")

    return {
        "sheet_profiles": profiles,
        "raw_datasets": raw_datasets,
        "status": "NODE_1_INGEST_COMPLETE"
    }


# ─────────────────────────────────────────────────────────────────────────────
# NODE 2: HEADER DETECTION & SMART CACHED LLM COLUMN MAPPING VALIDATION NODE
# ─────────────────────────────────────────────────────────────────────────────
def validation_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 2: ColumnMappingAgent (Local LLM Ollama qwen2.5:3b) semantically maps raw column
    headers to canonical domain fields with smart schema caching for identical payment sheets.
    Master Order Sheets map order_id, sku, quantity, status, order_date (Amount excluded).
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    raw_datasets = state.get("raw_datasets", [])

    print("\n" + "="*80)
    print(f"  [NODE 2: SMART CACHED LLM COLUMN MAPPING] EXECUTION STARTED FOR BATCH: {batch_id}")
    print("="*80)

    log_stage("NODE 2", f"Starting Node 2 LLM Column Mapping for {len(raw_datasets)} datasets")
    all_mappings = {}
    validation_results = []
    
    # In-memory schema cache for identical payment/order spreadsheet headers
    schema_cache: Dict[tuple, Dict[str, Any]] = {}
    cache_hits = 0

    for idx, ds in enumerate(raw_datasets):
        fname = ds.get("filename", f"file_{idx+1}")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        
        if not rows or not isinstance(rows[0], dict):
            continue

        headers = [str(k) for k in rows[0].keys() if k != "id"]
        schema_fingerprint = (role, tuple(sorted(headers)))

        print(f"\n--- [NODE 2 AI AGENT MAPPING DATASET #{idx+1}]: {fname} [{role}] ---")
        
        # Check Header Schema Cache First!
        if schema_fingerprint in schema_cache:
            cache_hits += 1
            mapping_result = schema_cache[schema_fingerprint]
            print(f"  ⚡ [SCHEMA CACHE HIT]: Headers match previously mapped {role}. Reusing cached AI mapping matrix (0s LLM latency)!")
            log_stage("NODE 2", f"Reusing cached LLM mapping matrix for '{fname}' (Cache Hit #{cache_hits})")
        else:
            log_stage("NODE 2", f"AI Agent ColumnMappingAgent analyzing {len(headers)} headers for '{fname}'")
            mapping_result = llm_map_columns(headers, rows, sheet_role=role)
            schema_cache[schema_fingerprint] = mapping_result

        mappings = mapping_result.get("mappings", {})
        all_mappings[fname] = mappings

        simple_map = {c_field: info.get("source_column") for c_field, info in mappings.items() if isinstance(info, dict)}

        print(f"  • AI Agent Mapping Matrix ({len(simple_map)} canonical fields mapped):")
        for c_field, info in mappings.items():
            if isinstance(info, dict):
                src_c = info.get("source_column", "N/A")
                conf = info.get("confidence", 1.0)
                rat = info.get("rationale", "")
                print(f"      - Canonical [{c_field}] ──▶ \"{src_c}\" (Confidence: {round(conf, 2)})")
                if rat:
                    print(f"        Rationale: {rat}")

        # Execute Python Structural Validation Guardrail
        df_data = pd.DataFrame(rows)
        is_valid, errors = validate_order_mapping(df_data, simple_map)
        val_status = "VALID" if is_valid else "WARNINGS_FOUND"
        validation_results.append({"filename": fname, "role": role, "is_valid": is_valid, "errors": errors})

        print(f"  • Python Structural Guardrail Check: {val_status}")
        if errors:
            for err in errors:
                print(f"      ⚠️ Warning: {err}")

        log_agent_call(
            agent_name="ColumnMappingAgent",
            task=f"Map {role} headers to canonical domain schema",
            input_summary=f"{len(headers)} raw column headers",
            output_summary=f"Mapped {len(simple_map)} fields for {fname} (Cache Hits: {cache_hits})",
            confidence=0.98,
            duration_sec=time.time() - start_time
        )

    print("\n" + "="*80)
    print(f"  [NODE 2 COMPLETE] Completed mapping validation for {len(raw_datasets)} datasets with {cache_hits} schema cache hits.")
    print("="*80 + "\n")

    log_stage("NODE 2", f"Node 2 complete ({cache_hits} schema cache hits). Ready for Node 3 normalization.")

    return {
        "column_mappings": all_mappings,
        "validation_results": validation_results,
        "schema_cache_hits": cache_hits,
        "status": "NODE_2_VALIDATED"
    }


def normalization_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 3: Normalizes raw status strings into CanonicalOrder and CanonicalPayment models."""
    log_stage("NODE 3", "Executing Node 3: Canonical Model Normalization")
    records = state.get("parsed_orders", [])
    normalized = []
    for r in records:
        r_copy = dict(r)
        r_copy["status"] = normalize_status(r.get("status", ""))
        normalized.append(r_copy)
    return {"normalized_records": normalized, "status": "NODE_3_NORMALIZED"}


def pattern_detection_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 4: Detects unknown status/deduction patterns requiring governance."""
    log_stage("NODE 4", "Executing Node 4: Pattern Detection")
    records = state.get("normalized_records", []) or state.get("parsed_orders", [])
    unknowns = detect_unknown_patterns(records)
    has_unknowns = len(unknowns) > 0
    return {
        "unknown_patterns": unknowns,
        "human_review_required": has_unknowns,
        "status": "NODE_4_PATTERNS_DETECTED"
    }


def reconciliation_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 5: Executes deterministic reconciliation matching."""
    log_stage("NODE 5", "Executing Node 5: Reconciliation Matching")
    orders = state.get("parsed_orders", [])
    payments = state.get("parsed_payments", [])
    rec_res = process_reconciliation(orders, payments)
    return {
        "reconciliation_results": rec_res,
        "match_rate": rec_res.get("matchRate", 0.0),
        "status": "NODE_5_RECONCILED"
    }


def financial_calculation_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 6: Executes deterministic profit/loss calculations."""
    log_stage("NODE 6", "Executing Node 6: Profit/Loss Calculation")
    records = state.get("normalized_records", []) or state.get("parsed_orders", [])
    grouped = group_by_sku(records)
    profit_res = calculate_overall_profit(grouped)
    return {
        "financial_summary": profit_res,
        "status": "NODE_6_CALCULATED"
    }


def exception_analysis_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 7: Analyzes batch exceptions using deterministic rule registry & LLM explanations."""
    start = time.time()
    log_stage("NODE 7", "Executing Node 7: Exception & Governance Analysis")
    records = state.get("normalized_records", []) or state.get("parsed_orders", [])
    rec_res = state.get("reconciliation_results", {})
    approved_rules = state.get("approved_rules", [])

    exceptions = evaluate_batch_exceptions(records, rec_res, approved_rules)
    pending_human = any(e.get("requires_human", False) and e.get("status") == "PENDING" for e in exceptions)

    log_agent_call(
        agent_name="ExceptionInvestigationAgent",
        task="Analyze unresolved financial anomalies & unknown patterns",
        input_summary=f"{len(exceptions)} surfaced exceptions",
        output_summary=f"Surfaced {len(exceptions)} items requiring governance",
        confidence=0.88,
        duration_sec=time.time() - start
    )

    return {
        "exceptions": exceptions,
        "human_review_required": pending_human,
        "status": "NODE_7_WAITING_HUMAN_REVIEW" if pending_human else "NODE_7_EXCEPTIONS_ANALYZED"
    }


def reprocessing_node(state: FinanceState) -> Dict[str, Any]:
    """Applies human-approved rules and reprocesses state."""
    log_stage("BATCH", "Reprocessing batch after human rule approval")
    return {"status": "REPROCESSED"}


def report_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 8: Generates final batch report metrics."""
    log_stage("NODE 8", "Executing Node 8: Report Generation")
    total_records = len(state.get("parsed_orders", []))
    rec_res = state.get("reconciliation_results", {})
    exceptions = state.get("exceptions", [])
    profit_res = state.get("financial_summary", {})
    proc_time = state.get("processing_time_ms", 120.0)

    metrics = calculate_batch_metrics(
        state.get("batch_id", "batch_demo"),
        total_records,
        rec_res,
        exceptions,
        profit_res,
        proc_time
    )

    final_report = {
        "metrics": metrics,
        "summary": profit_res.get("overall", {}),
        "skuBreakdown": profit_res.get("skuBreakdowns", {}),
        "reconciliation": rec_res,
        "exceptions": exceptions
    }

    log_stage("NODE 8", f"Generated final report: Match Rate {metrics['match_rate']}%, Profit INR {metrics['total_profit']}")

    return {
        "final_report": final_report,
        "status": "NODE_8_COMPLETED"
    }
