import io
import zipfile
import pandas as pd
from typing import List, Dict, Any, Tuple

def parse_csv_data(raw_text: str) -> Dict[str, Any]:
    """
    Parses tab or comma delimited CSV data into list of column key-value row dicts.
    """
    if not raw_text or not raw_text.strip():
        return {"success": False, "data": [], "errors": ["No data provided"]}

    try:
        delim = '\t' if '\t' in raw_text else ','
        df = pd.read_csv(io.StringIO(raw_text.strip()), sep=delim, dtype=str)
        
        parsed_data = []
        for index, row in df.iterrows():
            clean_row = {}
            for col in df.columns:
                val = str(row[col]).strip() if pd.notna(row[col]) else ""
                clean_row[str(col)] = val
            
            # Legacy keys mapping for compatibility
            clean_row["id"] = f"row-{index+1}"
            if "Sub Order No" in clean_row:
                clean_row["orderId"] = clean_row["Sub Order No"]
            if "SKU" in clean_row or "Supplier SKU" in clean_row:
                clean_row["skuId"] = clean_row.get("SKU") or clean_row.get("Supplier SKU")
            if "Reason for Credit Entry" in clean_row or "Live Order Status" in clean_row:
                clean_row["status"] = clean_row.get("Reason for Credit Entry") or clean_row.get("Live Order Status")
            if "Final Settlement Amount" in clean_row or "Amount" in clean_row:
                clean_row["amount"] = clean_row.get("Final Settlement Amount") or clean_row.get("Amount")
                
            parsed_data.append(clean_row)
                
        return {"success": True, "data": parsed_data, "errors": []}
    except Exception as e:
        return {"success": False, "data": [], "errors": [f"Parse error: {str(e)}"]}


def parse_excel_bytes(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
    """
    Parses all sheets in Excel file bytes (xlsx/xls), extracting full row dictionaries with headers.
    """
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        extracted_sheets = []

        for sheet_name in excel_file.sheet_names:
            df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            if len(df_raw) == 0:
                continue

            # Locate candidate header row (scan first 10 rows)
            header_row_idx = 0
            max_non_empty = 0
            for i in range(min(len(df_raw), 10)):
                row_vals = [str(val).strip() for val in df_raw.iloc[i] if pd.notna(val) and str(val).strip()]
                if len(row_vals) > max_non_empty:
                    max_non_empty = len(row_vals)
                    header_row_idx = i

            headers = [str(val).strip() if pd.notna(val) else f"col_{idx}" for idx, val in enumerate(df_raw.iloc[header_row_idx])]
            
            sheet_rows = []
            for i in range(header_row_idx + 1, len(df_raw)):
                row = df_raw.iloc[i]
                row_dict = {}
                non_empty_cnt = 0
                for c_idx, h_name in enumerate(headers):
                    val = str(row.iloc[c_idx]).strip() if c_idx < len(row) and pd.notna(row.iloc[c_idx]) else ""
                    if val and val.lower() != "nan":
                        row_dict[h_name] = val
                        non_empty_cnt += 1

                if non_empty_cnt > 0:
                    row_dict["id"] = f"row-{i}"
                    sheet_rows.append(row_dict)

            extracted_sheets.append({
                "sheet_name": sheet_name,
                "data": sheet_rows
            })

        # Combine all sheet data
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
                        res = parse_csv_data(file_bytes.decode('utf-8', errors='ignore'))
                    else:
                        res = parse_excel_bytes(file_bytes, filename)

                    if res["success"]:
                        extracted_files.append({
                            "filename": filename,
                            "data": res["data"]
                        })
                        all_data.extend(res["data"])
                    else:
                        all_errors.extend(res["errors"])

        return {
            "success": True,
            "files": extracted_files,
            "data": all_data,
            "errors": all_errors
        }
    except Exception as e:
        return {"success": False, "files": [], "data": [], "errors": [f"ZIP parse error: {str(e)}"]}
