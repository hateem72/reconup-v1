import pandas as pd
from typing import Tuple, List
from app.core.logging import log_stage

def detect_header_and_data_rows(df_raw: pd.DataFrame) -> Tuple[int, int, List[str]]:
    """
    Detects true (header_row_index, data_start_row_index, exact_headers).
    Scans candidate rows 0..9 looking for the row with the maximum count of valid string titles.
    Preserves exact, un-mangled column header strings from the source file.
    """
    best_row_idx = 0
    max_title_count = -1
    best_headers: List[str] = []

    for i in range(min(len(df_raw), 10)):
        row = df_raw.iloc[i]
        title_count = 0
        current_headers = []

        for c_idx, val in enumerate(row):
            val_str = str(val).strip() if pd.notna(val) else ""
            if val_str and val_str.lower() != "nan" and not val_str.isdigit():
                title_count += 1
                current_headers.append(val_str)
            else:
                current_headers.append(val_str if val_str else f"Column_{c_idx+1}")

        if title_count > max_title_count:
            max_title_count = title_count
            best_row_idx = i
            best_headers = current_headers

    header_row = best_row_idx
    data_start_row = best_row_idx + 1

    log_stage("PROFILER", f"Discovered True Header Row at index {header_row + 1} (1-based) with {max_title_count} title columns")
    return header_row, data_start_row, best_headers
