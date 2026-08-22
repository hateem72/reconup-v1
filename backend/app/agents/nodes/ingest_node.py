import pandas as pd
from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.profiler import profile_sheet
from app.core.logging import log_stage

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
