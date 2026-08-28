import time
import hashlib
import pandas as pd
from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.order_normalizer import llm_map_columns, validate_order_mapping
from app.core.logging import log_stage, log_agent_call
from app.core.redis_client import redis_client
from app.core.config import settings

def validation_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 2: ColumnMappingAgent (Local LLM Ollama qwen2.5:3b or Cloud LLM) semantically maps raw column
    headers to canonical domain fields with Redis-backed schema fingerprint caching.
    100% PURE LLM INTELLIGENCE — Zero hardcoded keyword rules used.
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    raw_datasets = state.get("raw_datasets", [])

    print("\n" + "="*80)
    print(f"  [NODE 2: PURE LLM COLUMN MAPPING] EXECUTION STARTED FOR BATCH: {batch_id}")
    print("="*80)

    log_stage("NODE 2", f"Starting Node 2 LLM Column Mapping for {len(raw_datasets)} essential datasets")
    all_mappings = {}
    validation_results = []
    cache_hits = 0

    for idx, ds in enumerate(raw_datasets):
        fname = ds.get("filename", f"file_{idx+1}")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        
        if not rows or not isinstance(rows[0], dict):
            continue

        headers = ds.get("exact_headers") or [str(k) for k in dict.fromkeys([k for r in rows[:10] for k in r.keys() if k != "id"])]
        
        # Build deterministic schema fingerprint cache key
        headers_str = ",".join(sorted(headers))
        fingerprint_hash = hashlib.sha256(f"{role}:{headers_str}".encode('utf-8')).hexdigest()[:16]
        cache_key = f"schema:{role}:{fingerprint_hash}"

        print(f"\n--- [NODE 2 AI AGENT MAPPING DATASET #{idx+1}]: {fname} [{role}] ---")
        
        # Check Redis Cache (or fallback RAM cache)
        mapping_result = redis_client.get_json(cache_key)
        
        if mapping_result:
            cache_hits += 1
            engine_name = "REDIS" if redis_client.is_connected else "SCHEMA"
            print(f"  ⚡ [{engine_name} CACHE HIT]: Headers match previously mapped {role}. Reusing cached AI mapping matrix (0s LLM latency)!")
            log_stage("NODE 2", f"⚡ {engine_name} Cache Hit for '{fname}': Reusing LLM mapping matrix (0s latency)")
        else:
            log_stage("NODE 2", f"AI Agent ColumnMappingAgent analyzing {len(headers)} headers for '{fname}'")
            mapping_result = llm_map_columns(headers, rows, sheet_role=role)
            redis_client.set_json(cache_key, mapping_result, ttl_seconds=settings.REDIS_TTL_SECONDS)

        mappings = mapping_result.get("mappings", {})
        all_mappings[fname] = mappings

        simple_map = {c_field: info.get("source_column") for c_field, info in mappings.items() if isinstance(info, dict)}

        print(f"  • AI Agent Mapping Matrix ({len(simple_map)} canonical fields mapped):")
        for c_field, info in mappings.items():
            if isinstance(info, dict):
                src_c = info.get("source_column", "N/A")
                conf = info.get("confidence")
                conf_val = float(conf) if conf is not None else 0.95
                rat = info.get("rationale", "")
                print(f"      - Canonical [{c_field}] ──▶ \"{src_c}\" (Confidence: {round(conf_val, 2)})")
                log_stage("NODE 2", f"Dataset '{fname}': Canonical [{c_field}] ──▶ '{src_c}' (Confidence: {round(conf_val, 2)})")

        df_data = pd.DataFrame(rows)
        is_valid, errors = validate_order_mapping(df_data, simple_map)
        val_status = "VALID" if is_valid else "WARNINGS_FOUND"

        print(f"  • Python Structural Guardrail Check: {val_status}")
        log_stage("NODE 2", f"Python Structural Guardrail Result for '{fname}': {val_status}")

        log_agent_call(
            agent_name="ColumnMappingAgent",
            task=f"Map {role} headers to canonical domain schema",
            input_summary=f"{len(headers)} raw column headers",
            output_summary=f"Mapped {len(mappings)} fields for {fname} (Cache Hits: {cache_hits})",
            confidence=0.98,
            duration_sec=time.time() - start_time
        )

        validation_results.append({
            "filename": fname,
            "role": role,
            "header_count": len(headers),
            "mapped_fields": simple_map,
            "validation_status": val_status,
            "warnings": errors
        })

    print("\n" + "="*80)
    print(f"  [NODE 2 COMPLETE] Completed mapping validation for {len(raw_datasets)} essential datasets with {cache_hits} schema cache hits.")
    print("="*80 + "\n")

    log_stage("NODE 2", f"Node 2 complete ({cache_hits} schema cache hits). Ready for Node 3 normalization.")

    return {
        "column_mappings": all_mappings,
        "validation_results": validation_results,
        "cache_hits": cache_hits,
        "status": "NODE_2_MAPPED"
    }
