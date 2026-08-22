import io
import re
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from app.schemas.canonical import ColumnProfile, SheetProfile
from app.core.logging import log_stage

def list_sheets(file_bytes: bytes, filename: str = "") -> List[Dict[str, Any]]:
    """Discovers all sheet names and indices in an uploaded Excel file."""
    log_stage("ORDER", f"Discovering sheets in workbook: {filename}")
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        sheets = []
        for idx, name in enumerate(excel_file.sheet_names):
            sheets.append({"name": name, "index": idx})
        log_stage("ORDER", f"Discovered {len(sheets)} sheets: {[s['name'] for s in sheets]}")
        return sheets
    except Exception as e:
        log_stage("ORDER", f"Failed to list sheets: {str(e)}", level="error")
        return [{"name": "Sheet1", "index": 0}]


def profile_column(series: pd.Series, col_name: str, col_idx: int) -> ColumnProfile:
    """Profiles statistical and semantic characteristics of a single Pandas Series."""
    clean_series = series.dropna()
    total_count = len(series)
    null_count = int(series.isna().sum())
    null_pct = float(null_count / total_count * 100.0) if total_count > 0 else 100.0

    unique_count = int(clean_series.nunique())
    uniqueness_ratio = float(unique_count / len(clean_series)) if len(clean_series) > 0 else 0.0

    sample_vals = [str(val).strip() for val in clean_series.head(5).tolist()]

    # Data Type Detection
    numeric_count = 0
    date_count = 0
    identifier_count = 0

    for val in clean_series.head(20):
        val_str = str(val).strip()
        # Check numeric
        cleaned_num = re.sub(r'[₹$,\s]', '', val_str)
        try:
            float(cleaned_num)
            numeric_count += 1
        except ValueError:
            pass

        # Check date
        if re.search(r'\d{2,4}[-/\.]\d{1,2}[-/\.]\d{1,4}', val_str) or '202' in val_str:
            date_count += 1

        # Check identifier
        if re.search(r'^(ORD|SKU|TRX|INV|SUB|PAY|SET)[A-Z0-9_-]+$', val_str, re.I) or (len(val_str) > 5 and val_str.isalnum()):
            identifier_count += 1

    sample_len = min(len(clean_series), 20)
    numeric_like = (numeric_count / sample_len > 0.6) if sample_len > 0 else False
    date_like = (date_count / sample_len > 0.4) if sample_len > 0 else False
    identifier_like = (identifier_count / sample_len > 0.5) if sample_len > 0 else False

    return ColumnProfile(
        column_name=str(col_name),
        column_index=col_idx,
        dtype=str(series.dtype),
        null_count=null_count,
        null_percentage=round(null_pct, 2),
        unique_count=unique_count,
        uniqueness_ratio=round(uniqueness_ratio, 4),
        sample_values=sample_vals,
        date_like=date_like,
        numeric_like=numeric_like,
        identifier_like=identifier_like
    )


def profile_sheet(df_raw: pd.DataFrame, sheet_name: str, sheet_idx: int) -> SheetProfile:
    """Profiles a sheet raw dataframe, identifying candidate header rows and column profiles."""
    log_stage("ORDER", f"Profiling sheet: '{sheet_name}' ({len(df_raw)} rows x {len(df_raw.columns)} cols)")
    row_count, col_count = df_raw.shape

    # 1. Preview rows (first 6 rows)
    preview_rows = []
    for i in range(min(row_count, 6)):
        row_vals = [val if pd.notna(val) else "" for val in df_raw.iloc[i].tolist()]
        preview_rows.append(row_vals)

    # 2. Candidate Header Rows (Scan first 10 rows)
    candidate_header_rows = []
    for i in range(min(row_count, 10)):
        row_vals = df_raw.iloc[i].dropna().tolist()
        str_vals = [str(v).strip() for v in row_vals if str(v).strip()]
        # Header candidate has multiple non-empty string column titles
        if len(str_vals) >= max(2, int(col_count * 0.3)):
            candidate_header_rows.append(i + 1) # 1-indexed for human readability

    if not candidate_header_rows:
        candidate_header_rows = [1]

    # 3. Column Profiles
    column_profiles = []
    for c_idx in range(col_count):
        col_name = str(df_raw.columns[c_idx])
        col_prof = profile_column(df_raw.iloc[:, c_idx], col_name, c_idx)
        column_profiles.append(col_prof)

    return SheetProfile(
        sheet_name=sheet_name,
        sheet_index=sheet_idx,
        row_count=row_count,
        column_count=col_count,
        preview_rows=preview_rows,
        candidate_header_rows=candidate_header_rows,
        column_profiles=column_profiles
    )
