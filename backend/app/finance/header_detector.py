import pandas as pd
from typing import Tuple
from app.core.logging import log_stage

def detect_header_and_data_rows(df_raw: pd.DataFrame) -> Tuple[int, int]:
    """
    Detects (header_row_index, data_start_row_index) 0-indexed.
    Scans candidate rows 0..9 looking for row with maximum string title headers.
    """
    log_stage("ORDER", "Detecting header row candidates")
    best_row_idx = 0
    max_non_empty = 0

    for i in range(min(len(df_raw), 10)):
        row = df_raw.iloc[i]
        non_empty = sum(1 for val in row if pd.notna(val) and str(val).strip() != "")
        if non_empty > max_non_empty:
            max_non_empty = non_empty
            best_row_idx = i

    header_row = best_row_idx
    data_start_row = best_row_idx + 1

    log_stage("ORDER", f"Selected header row: {header_row + 1} (1-based), data starts at row: {data_start_row + 1}")
    return header_row, data_start_row
