import pandas as pd
from typing import Tuple, List
from app.core.logging import log_stage

KEY_HEADER_TERMS = [
    "sub order no", "sub order number", "order id", "order_id", "supplier sku", "sku", 
    "live order status", "status", "transaction id", "payment date", 
    "dispatch date", "order date", "product name", "final settlement amount",
    "total sale amount", "listing price", "quantity", "catalog id"
]

def score_header_candidate_row(row: pd.Series) -> Tuple[float, int, List[str]]:
    score = 0.0
    valid_titles = 0
    headers = []

    for c_idx, val in enumerate(row):
        val_str = str(val).strip() if pd.notna(val) else ""
        if val_str and val_str.lower() != "nan":
            headers.append(val_str)
            valid_titles += 1
            val_lower = val_str.lower()

            # Domain keyword match (+50 points each)
            if any(term in val_lower for term in KEY_HEADER_TERMS):
                score += 50.0

            # Single character letter penalty (-5) or formula penalty (-10)
            if len(val_str) == 1 and val_str.isalpha():
                score -= 5.0
            elif "(" in val_str and "+" in val_str:
                score -= 10.0
            elif not val_str.isdigit():
                score += 2.0
        else:
            headers.append(f"Column_{c_idx+1}")

    score += valid_titles * 1.5
    return score, valid_titles, headers


def detect_header_and_data_rows(df_raw: pd.DataFrame) -> Tuple[int, int, List[str]]:
    """
    Detects true (header_row_index, data_start_row_index, exact_headers).
    Scans candidate rows 0..15 using domain-aware header scoring to identify the
    true header row (e.g. Row 4 with 'Sub Order No', 'Supplier SKU', 'Live Order Status')
    instead of formula/disclaimer rows.
    Preserves exact, un-mangled column header strings from the source file.
    """
    best_row_idx = 0
    max_score = -999.0
    best_headers: List[str] = []
    best_title_count = 0

    scan_limit = min(len(df_raw), 15)
    for i in range(scan_limit):
        row = df_raw.iloc[i]
        score, title_cnt, headers = score_header_candidate_row(row)

        if score > max_score:
            max_score = score
            best_row_idx = i
            best_headers = headers
            best_title_count = title_cnt

    header_row = best_row_idx
    data_start_row = best_row_idx + 1

    log_stage("PROFILER", f"Discovered True Header Row at index {header_row + 1} (1-based) with {len(best_headers)} total columns ({best_title_count} named headers)")
    return header_row, data_start_row, best_headers
