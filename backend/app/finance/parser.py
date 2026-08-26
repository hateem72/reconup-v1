import io
import zipfile
import pandas as pd
from typing import List, Dict, Any, Tuple
from app.finance.header_detector import detect_header_and_data_rows

def parse_csv_data(raw_text: str) -> Dict[str, Any]:
    """
    Parses tab or comma delimited CSV data into list of column key-value row dicts.
    Preserves exact original column header names from the CSV file.
    """
    if not raw_text or not raw_text.strip():
        return {"success": False, "data": [], "errors": ["No data provided"]}

    try:
        delim = '\t' if '\t' in raw_text else ','
        df = pd.read_csv(io.StringIO(raw_text.strip()), sep=delim, dtype=str)
        
        headers = [str(c).strip() for c in df.columns]
        parsed_data = []
        for index, row in df.iterrows():
            clean_row = {}
            for col in df.columns:
                col_name = str(col).strip()
                val = str(row[col]).strip() if pd.notna(row[col]) else ""
                clean_row[col_name] = val if val.lower() != "nan" else ""
            
            clean_row["id"] = f"row-{index+1}"
            parsed_data.append(clean_row)
                
        return {"success": True, "data": parsed_data, "exact_headers": headers, "errors": []}
    except Exception as e:
        return {"success": False, "data": [], "exact_headers": [], "errors": [f"Parse error: {str(e)}"]}


def parse_excel_bytes(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Parses all sheets in Excel file bytes (xlsx/xls).
    Uses true header row detection to extract exact, un-mangled header column names.
    Preserves full header key coverage across all rows.
    """
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        extracted_sheets = []

        for sheet_name in excel_file.sheet_names:
            df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            if len(df_raw) == 0:
                continue

            header_row_idx, data_start_idx, exact_headers = detect_header_and_data_rows(df_raw)

            sheet_rows = []
            for i in range(data_start_idx, len(df_raw)):
                row = df_raw.iloc[i]
                row_dict = {}
                non_empty_cnt = 0
                for c_idx, h_name in enumerate(exact_headers):
                    val = str(row.iloc[c_idx]).strip() if c_idx < len(row) and pd.notna(row.iloc[c_idx]) else ""
                    cleaned_val = val if val.lower() != "nan" else ""
                    row_dict[h_name] = cleaned_val
                    if cleaned_val:
                        non_empty_cnt += 1

                if non_empty_cnt > 0:
                    row_dict["id"] = f"row-{i+1}"
                    sheet_rows.append(row_dict)

            extracted_sheets.append({
                "sheet_name": sheet_name,
                "data": sheet_rows,
                "header_row_index": header_row_idx + 1,
                "exact_headers": exact_headers
            })

        all_rows = []
        for s in extracted_sheets:
            all_rows.extend(s["data"])

        return {
            "success": True,
            "sheets": extracted_sheets,
            "data": all_rows,
            "errors": []
        }
    except Exception as e:
        return {"success": False, "sheets": [], "data": [], "errors": [f"Excel parse error: {str(e)}"]}


def parse_zip_file(zip_bytes: bytes) -> Dict[str, Any]:
    """
    Parses a ZIP file containing multiple Excel / CSV files.
    """
    try:
        extracted_files = []
        all_data = []
        all_errors = []
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for filename in z.namelist():
                if filename.endswith(('.xlsx', '.xls', '.csv')) and not filename.startswith('__MACOSX'):
                    file_bytes = z.read(filename)
                    if filename.endswith('.csv'):
                        raw_text = file_bytes.decode('utf-8', errors='ignore')
                        res = parse_csv_data(raw_text)
                        if res["success"]:
                            extracted_files.append({"filename": filename, "data": res["data"], "exact_headers": res.get("exact_headers", [])})
                            all_data.extend(res["data"])
                    else:
                        res = parse_excel_bytes(file_bytes, filename)
                        if res["success"]:
                            for s in res.get("sheets", []):
                                f_name = f"{filename} [{s['sheet_name']}]"
                                extracted_files.append({"filename": f_name, "data": s["data"], "exact_headers": s.get("exact_headers", [])})
                                all_data.extend(s["data"])

        return {
            "success": True,
            "files": extracted_files,
            "data": all_data,
            "errors": all_errors
        }
    except Exception as e:
        return {"success": False, "files": [], "data": [], "errors": [f"Zip parse error: {str(e)}"]}
