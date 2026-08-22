import time
import io
import pandas as pd
from typing import Dict, Any, List
from app.agents.state import FinanceState
from app.finance.profiler import list_sheets, profile_sheet
from app.finance.normalizer import normalize_status, llm_normalize_statuses, clean_quantity, parse_numeric_amount
from app.finance.validator import validate_sales_data
from app.finance.order_normalizer import llm_map_columns, validate_order_mapping, normalize_canonical_orders
from app.finance.payment_normalizer import auto_map_payment_columns, normalize_canonical_payments
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.finance.reconciliation import process_reconciliation
from app.finance.exception_detector import evaluate_batch_exceptions, detect_unknown_patterns
from app.finance.metrics import calculate_batch_metrics
from app.schemas.canonical import CanonicalOrder, CanonicalPayment
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
                conf = info.get("confidence")
                conf_val = float(conf) if conf is not None else 1.0
                rat = info.get("rationale", "")
                print(f"      - Canonical [{c_field}] ──▶ \"{src_c}\" (Confidence: {round(conf_val, 2)})")
                if rat:
                    print(f"        Rationale: {rat}")

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


# ─────────────────────────────────────────────────────────────────────────────
# NODE 3: CANONICAL MODEL NORMALIZATION & LLM STATUS CLASSIFICATION NODE
# ─────────────────────────────────────────────────────────────────────────────
def normalization_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 3: StatusNormalizationAgent (Local LLM Ollama qwen2.5:3b) categorizes unique raw status
    strings into canonical categories (Delivered, Return, RTO, Cancelled, Shipped, Return_Initiated, Claim).
    Normalizes raw rows into CanonicalOrder and CanonicalPayment models with 100% source traceability.
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    raw_datasets = state.get("raw_datasets", [])
    column_mappings = state.get("column_mappings", {})

    print("\n" + "="*80)
    print(f"  [NODE 3: CANONICAL NORMALIZATION & LLM STATUS CLASSIFICATION] STARTED FOR BATCH: {batch_id}")
    print("="*80)

    log_stage("NODE 3", f"Starting Node 3 Normalization across {len(raw_datasets)} datasets")

    # 1. Collect all unique raw status values across all datasets
    raw_statuses = set()
    for ds in raw_datasets:
        fname = ds.get("filename", "")
        rows = ds.get("data", [])
        mapping = column_mappings.get(fname, {})
        status_col = mapping.get("status", {}).get("source_column") if isinstance(mapping.get("status"), dict) else None
        
        # Fallback scan for status column if mapping missing or empty
        if not status_col and rows and isinstance(rows[0], dict):
            status_col = next((k for k in rows[0].keys() if "status" in k.lower() or "credit" in k.lower()), None)

        if status_col:
            for r in rows:
                val = str(r.get(status_col, "")).strip()
                if val and val.lower() != "nan":
                    raw_statuses.add(val)

    print(f"\n--- [NODE 3 AI AGENT: StatusNormalizationAgent] ---")
    print(f"  • Extracted {len(raw_statuses)} unique raw status strings across datasets.")

    # 2. Invoke Local LLM StatusNormalizationAgent
    status_map = llm_normalize_statuses(list(raw_statuses))

    print(f"  • AI Status Categorization Matrix ({len(status_map)} categories mapped):")
    for raw_s, info in status_map.items():
        cat = info.get("canonical_category", raw_s) if isinstance(info, dict) else raw_s
        conf = info.get("confidence") if isinstance(info, dict) else 1.0
        conf_val = float(conf) if conf is not None else 1.0
        print(f"      - \"{raw_s}\" ──▶ Canonical Category: [{cat}] (Confidence: {round(conf_val, 2)})")

    # 3. Generate CanonicalOrder and CanonicalPayment Domain Models
    canonical_orders: List[CanonicalOrder] = []
    canonical_payments: List[CanonicalPayment] = []
    master_order_ids = set()

    for ds in raw_datasets:
        fname = ds.get("filename", "")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        mapping = column_mappings.get(fname, {})

        simple_map = {c_f: info.get("source_column") for c_f, info in mapping.items() if isinstance(info, dict)}
        
        order_id_col = simple_map.get("order_id") or "Sub Order No"
        sku_col = simple_map.get("sku") or "SKU"
        qty_col = simple_map.get("quantity") or "Quantity"
        status_col = simple_map.get("status") or "Live Order Status"
        date_col = simple_map.get("order_date") or simple_map.get("payment_date") or "Order Date"
        amount_col = simple_map.get("amount") or "Final Settlement Amount"

        if role == "MASTER ORDER SHEET":
            print(f"\n--- [NORMALIZING MASTER ORDER SHEET]: {fname} ({len(rows)} rows) ---")
            for idx, r in enumerate(rows):
                oid = str(r.get(order_id_col, "")).strip()
                if not oid or oid.lower() in ("nan", "null", "none"):
                    continue

                master_order_ids.add(oid)
                raw_st = str(r.get(status_col, "")).strip()
                norm_cat = status_map.get(raw_st, {}).get("canonical_category", raw_st) if isinstance(status_map.get(raw_st), dict) else normalize_status(raw_st)

                c_ord = CanonicalOrder(
                    order_id=oid,
                    sku=str(r.get(sku_col, "")).strip(),
                    product_name=str(r.get("Product Name", r.get("product_name", ""))).strip(),
                    quantity=clean_quantity(r.get(qty_col, 1)),
                    status=norm_cat,
                    order_date=str(r.get(date_col, "")).strip(),
                    source_platform="Meesho/Generic",
                    source_file=fname,
                    source_sheet="OrderSheet",
                    source_row=idx + 2,
                    raw_data={str(k): str(v) for k, v in r.items() if str(v).lower() != "nan"}
                )
                canonical_orders.append(c_ord)

        else:
            print(f"\n--- [NORMALIZING PAYMENT SETTLEMENT SHEET]: {fname} ({len(rows)} multi-event rows) ---")
            for idx, r in enumerate(rows):
                oid = str(r.get(order_id_col, "")).strip()
                if not oid or oid.lower() in ("nan", "null", "none"):
                    continue

                raw_st = str(r.get(status_col, "")).strip()
                norm_cat = status_map.get(raw_st, {}).get("canonical_category", raw_st) if isinstance(status_map.get(raw_st), dict) else normalize_status(raw_st)
                amt_val = parse_numeric_amount(r.get(amount_col, 0.0))

                c_pmt = CanonicalPayment(
                    transaction_id=str(r.get("Transaction ID", r.get("transaction_id", f"pmt-{idx+1}-{oid}"))).strip(),
                    order_id=oid,
                    settlement_amount=amt_val,
                    status=norm_cat,
                    quantity=clean_quantity(r.get(qty_col, 1)),
                    sku=str(r.get(sku_col, "")).strip(),
                    payment_date=str(r.get(date_col, "")).strip(),
                    source_platform="Meesho/Generic",
                    source_file=fname,
                    source_sheet="PaymentSheet",
                    source_row=idx + 2,
                    raw_data={str(k): str(v) for k, v in r.items() if str(v).lower() != "nan"}
                )
                canonical_payments.append(c_pmt)

    # 4. Highlight Anchor Order Matching vs Historical Payments
    historical_payments_count = sum(1 for p in canonical_payments if p.order_id not in master_order_ids)

    print("\n" + "="*80)
    print(f"  [NODE 3 SUMMARY]:")
    print(f"  • Normalized Canonical Orders (Master Anchor): {len(canonical_orders)} records ({len(master_order_ids)} unique order IDs)")
    print(f"  • Normalized Canonical Payments (Multi-Event): {len(canonical_payments)} settlement event lines")
    print(f"  • Payment Rows Matching Master Anchor: {len(canonical_payments) - historical_payments_count} lines")
    print(f"  • Historical Payment Lines (Previous Months): {historical_payments_count} lines")
    print("="*80 + "\n")

    log_agent_call(
        agent_name="StatusNormalizationAgent",
        task="Categorize raw statuses into canonical order lifecycle states",
        input_summary=f"{len(raw_statuses)} unique raw status strings",
        output_summary=f"Categorized into {len(status_map)} categories",
        confidence=0.97,
        duration_sec=time.time() - start_time
    )

    log_stage("NODE 3", f"Node 3 complete. Normalized {len(canonical_orders)} orders and {len(canonical_payments)} payments.")

    return {
        "canonical_orders": canonical_orders,
        "canonical_payments": canonical_payments,
        "master_order_ids_count": len(master_order_ids),
        "historical_payments_count": historical_payments_count,
        "status_mappings": status_map,
        "status": "NODE_3_NORMALIZED"
    }


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
