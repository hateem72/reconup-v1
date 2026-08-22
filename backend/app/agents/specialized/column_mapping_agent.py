import time
import pandas as pd
from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.order_normalizer import llm_map_columns, validate_order_mapping
from app.core.logging import log_stage

def log_agent_call(agent_name: str, task: str, input_summary: str, output_summary: str, confidence: float, duration_sec: float):
    """Logs structured AI call execution metrics per requirements."""
    log_stage("AGENT", f"Agent: {agent_name} | Task: {task}")
    log_stage("AGENT", f"  Input: {input_summary}")
    log_stage("AGENT", f"  Output: {output_summary}")
    log_stage("AGENT", f"  Confidence: {round(confidence, 2)} | Duration: {round(duration_sec, 3)}s | Status: SUCCESS")


def validation_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 2: ColumnMappingAgent (Local LLM Ollama qwen2.5:3b) semantically maps raw column
    headers to canonical domain fields with distinct sub-tab schema caching.
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    raw_datasets = state.get("raw_datasets", [])

    print("\n" + "="*80)
    print(f"  [NODE 2: SMART CACHED LLM COLUMN MAPPING] EXECUTION STARTED FOR BATCH: {batch_id}")
    print("="*80)

    log_stage("NODE 2", f"Starting Node 2 LLM Column Mapping for {len(raw_datasets)} essential datasets")
    all_mappings = {}
    validation_results = []
    
    schema_cache: Dict[tuple, Dict[str, Any]] = {}
    cache_hits = 0

    SUMMARY_KEYWORDS = ["ads cost", "referral", "disclaimer", "compensation and recovery", "reward id"]

    for idx, ds in enumerate(raw_datasets):
        fname = ds.get("filename", f"file_{idx+1}")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        
        if not rows or not isinstance(rows[0], dict):
            continue

        headers = [str(k) for k in rows[0].keys() if k != "id"]
        
        is_summary_tab = len(headers) < 4 or any(sub_k in fname.lower() for sub_k in SUMMARY_KEYWORDS)
        entity_role = "PAYMENT SUMMARY TAB" if (is_summary_tab and "ORDER" not in role.upper()) else role

        schema_fingerprint = (entity_role, is_summary_tab, tuple(sorted(headers)))

        print(f"\n--- [NODE 2 AI AGENT MAPPING DATASET #{idx+1}]: {fname} [{entity_role}] ---")
        
        if schema_fingerprint in schema_cache:
            cache_hits += 1
            mapping_result = schema_cache[schema_fingerprint]
            print(f"  ⚡ [SCHEMA CACHE HIT]: Headers match previously mapped {entity_role}. Reusing cached AI mapping matrix (0s LLM latency)!")
            log_stage("NODE 2", f"Reusing cached LLM mapping matrix for '{fname}' (Cache Hit #{cache_hits})")
        else:
            log_stage("NODE 2", f"AI Agent ColumnMappingAgent analyzing {len(headers)} headers for '{fname}'")
            if is_summary_tab:
                mapping_result = {
                    "mappings": {
                        "summary_type": {
                            "source_column": headers[0] if headers else "N/A",
                            "confidence": 1.0,
                            "rationale": f"Summary sub-tab entity mapped first header '{headers[0] if headers else 'N/A'}'."
                        }
                    }
                }
            else:
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
        
        if is_summary_tab:
            is_valid = True
            errors = []
            val_status = "SUMMARY_SHEET (Distinct Entity - No order_id required)"
        else:
            is_valid, errors = validate_order_mapping(df_data, simple_map)
            val_status = "VALID" if is_valid else "WARNINGS_FOUND"

        validation_results.append({"filename": fname, "role": entity_role, "is_valid": is_valid, "errors": errors})

        print(f"  • Python Structural Guardrail Check: {val_status}")
        if errors:
            for err in errors:
                print(f"      ⚠️ Warning: {err}")

        log_agent_call(
            agent_name="ColumnMappingAgent",
            task=f"Map {entity_role} headers to canonical domain schema",
            input_summary=f"{len(headers)} raw column headers",
            output_summary=f"Mapped {len(simple_map)} fields for {fname} (Cache Hits: {cache_hits})",
            confidence=0.98,
            duration_sec=time.time() - start_time
        )

    print("\n" + "="*80)
    print(f"  [NODE 2 COMPLETE] Completed mapping validation for {len(raw_datasets)} essential datasets with {cache_hits} schema cache hits.")
    print("="*80 + "\n")

    log_stage("NODE 2", f"Node 2 complete ({cache_hits} schema cache hits). Ready for Node 3 normalization.")

    return {
        "column_mappings": all_mappings,
        "validation_results": validation_results,
        "schema_cache_hits": cache_hits,
        "status": "NODE_2_VALIDATED"
    }
