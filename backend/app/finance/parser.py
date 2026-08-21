import io
import zipfile
import pandas as pd
import openpyxl
from typing import List, Dict, Any, Tuple

def parse_csv_data(raw_text: str) -> Dict[str, Any]:
    """
    Parses tab or comma delimited CSV data.
    """
    if not raw_text or not raw_text.strip():
        return {"success": False, "data": [], "errors": ["No data provided"]}

    try:
        # Determine delimiter (tab if present, else comma)
        delim = '\t' if '\t' in raw_text else ','
        df = pd.read_csv(io.StringIO(raw_text.strip()), sep=delim, dtype=str)
        
        parsed_data = []
        for index, row in df.iterrows():
            cols = list(row.values)
            sku_id = str(cols[0]).strip() if len(cols) > 0 and pd.notna(cols[0]) else ""
            status = str(cols[1]).strip() if len(cols) > 1 and pd.notna(cols[1]) else ""
            amount = str(cols[2]).strip() if len(cols) > 2 and pd.notna(cols[2]) else ""
            
            if sku_id or status or amount:
                parsed_data.append({
                    "id": f"row-{index}",
                    "skuId": sku_id,
                    "status": status,
                    "amount": amount,
                    "quantity": "1",
                    "rowNumber": index + 1
                })
                
        return {"success": True, "data": parsed_data, "errors": []}
    except Exception as e:
        return {"success": False, "data": [], "errors": [f"Parse error: {str(e)}"]}


def parse_excel_bytes(file_bytes: bytes) -> Dict[str, Any]:
    """
    Parses Excel file bytes (xlsx/xls).
    Dynamically scans header rows to locate:
    - Supplier SKU
    - Live Order Status
    - Quantity
    - Final Settlement Amount
    """
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        sheet_names = excel_file.sheet_names
        
        # Target sheet with 'order payments' or fallback
        target_sheet = next((s for s in sheet_names if 'order payments' in s.lower()), None)
        if not target_sheet:
            target_sheet = sheet_names[1] if len(sheet_names) > 1 else sheet_names[0]
            
        df_raw = pd.read_excel(excel_file, sheet_name=target_sheet, header=None)
        
        header_row_idx = -1
        sku_col = -1
        status_col = -1
        qty_col = -1
        amount_col = -1

        # Scan first 10 rows for matching headers
        for i in range(min(len(df_raw), 10)):
            row_vals = [str(val).lower() if pd.notna(val) else "" for val in df_raw.iloc[i]]
            
            s_idx = next((idx for idx, v in enumerate(row_vals) if 'supplier sku' in v or 'sku' in v), -1)
            st_idx = next((idx for idx, v in enumerate(row_vals) if 'live order status' in v or 'status' in v), -1)
            q_idx = next((idx for idx, v in enumerate(row_vals) if 'quantity' in v or 'qty' in v), -1)
            a_idx = next((idx for idx, v in enumerate(row_vals) if 'final settlement amount' in v or 'amount' in v), -1)

            if s_idx != -1 and st_idx != -1 and a_idx != -1:
                header_row_idx = i
                sku_col = s_idx
                status_col = st_idx
                qty_col = q_idx if q_idx != -1 else s_idx + 2
                amount_col = a_idx
                break

        if header_row_idx == -1:
            # Fallback to standard columns 0, 1, 2, 3 if explicit headers not matched
            header_row_idx = 0
            sku_col, status_col, qty_col, amount_col = 0, 1, 2, 3

        extracted_data = []
        data_start_idx = header_row_idx + 1
        
        for i in range(data_start_idx, len(df_raw)):
            row = df_raw.iloc[i]
            
            sku_val = str(row.iloc[sku_col]).strip() if sku_col < len(row) and pd.notna(row.iloc[sku_col]) else ""
            status_val = str(row.iloc[status_col]).strip() if status_col < len(row) and pd.notna(row.iloc[status_col]) else ""
            qty_val = str(row.iloc[qty_col]).strip() if qty_col < len(row) and pd.notna(row.iloc[qty_col]) else "1"
            amount_val = str(row.iloc[amount_col]).strip() if amount_col < len(row) and pd.notna(row.iloc[amount_col]) else ""

            # Check Column AP (idx 41) & AQ (idx 42) for fallback status
            col_ap = str(row.iloc[41]).strip() if len(row) > 41 and pd.notna(row.iloc[41]) else ""
            col_aq = str(row.iloc[42]).strip() if len(row) > 42 and pd.notna(row.iloc[42]) else ""

            if not status_val:
                if "affiliate" in col_aq.lower():
                    status_val = "Affiliate Fees"
                elif amount_val:
                    try:
                        amt_num = float(amount_val.replace("₹", "").replace(",", "").strip())
                        if amt_num > 0 and (col_ap or "compensation" in str(row).lower() or "claim" in str(row).lower()):
                            status_val = "Claim"
                    except ValueError:
                        pass

            if not sku_val and not status_val and not amount_val:
                continue

            extracted_data.append({
                "id": f"row-{i}",
                "skuId": sku_val,
                "status": status_val,
                "quantity": qty_val,
                "amount": amount_val,
                "rowNumber": i + 1
            })

        return {"success": True, "data": extracted_data, "errors": []}
    except Exception as e:
        return {"success": False, "data": [], "errors": [f"Excel parse error: {str(e)}"]}


def parse_zip_file(zip_bytes: bytes) -> Dict[str, Any]:
    """
    Parses a ZIP file containing multiple Excel files.
    """
    try:
        all_data = []
        all_errors = []
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for filename in z.namelist():
                if filename.endswith(('.xlsx', '.xls')) and not filename.startswith('__MACOSX'):
                    file_data = z.read(filename)
                    res = parse_excel_bytes(file_data)
                    if res["success"]:
                        all_data.extend(res["data"])
                    else:
                        all_errors.extend(res["errors"])

        if not all_data and all_errors:
            return {"success": False, "data": [], "errors": all_errors}
            
        return {"success": True, "data": all_data, "errors": all_errors}
    except Exception as e:
        return {"success": False, "data": [], "errors": [f"ZIP parse error: {str(e)}"]}
