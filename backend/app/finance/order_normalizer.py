import re
import json
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from app.schemas.canonical import CanonicalOrder, ColumnMappingResult, ColumnMapping
from app.finance.normalizer import normalize_status, clean_quantity
from app.finance.payment_normalizer import auto_map_payment_columns
from app.core.logging import log_stage

CANONICAL_ORDER_KEYWORDS = {
    "order_id": ["sub order number", "sub order no", "order id", "order number", "order_id", "order_no", "order reference"],
    "sku": ["supplier sku", "seller sku", "sku", "product sku", "sku_id", "item sku"],
    "product_name": ["product name", "title", "product", "item name", "description"],
    "quantity": ["quantity", "qty", "units", "item quantity"],
    "status": ["live order status", "reason for credit entry", "status", "shipment status", "order status", "current status"],
    "dispatch_date": ["dispatch date", "shipped date", "dispatch timestamp", "dispatch_date"],
    "order_date": ["order date", "order timestamp", "created date", "order_date"]
}

def auto_map_order_columns(headers: List[str]) -> Dict[str, str]:
    """
    Deterministically maps source headers to canonical order fields based on exact & fuzzy keyword matching.
    Amount is intentionally excluded from Master Order Sheets.
    """
    mapping = {}
    lower_headers = [str(h).lower().strip() for h in headers]

    for canonical_field, keywords in CANONICAL_ORDER_KEYWORDS.items():
        matched_col = ""
        for kw in keywords:
            if kw in lower_headers:
                matched_col = headers[lower_headers.index(kw)]
                break
        if not matched_col:
            for kw in keywords:
                for idx, h_lower in enumerate(lower_headers):
                    if kw in h_lower:
                        matched_col = headers[idx]
                        break
                if matched_col:
                    break
        if matched_col:
            mapping[canonical_field] = matched_col

    return mapping


def parse_json_from_llm_text(text: str) -> Optional[Dict[str, Any]]:
    """Robustly extracts and parses JSON objects from LLM output, handling markdown codeblocks and extra text."""
    if not text:
        return None

    clean_text = re.sub(r'```(?:json)?', '', text).strip()
    start_idx = clean_text.find('{')
    end_idx = clean_text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = clean_text[start_idx:end_idx + 1]
        json_str = re.sub(r',\s*([\}\]])', r'\1', json_str)
        try:
            return json.loads(json_str)
        except Exception:
            pass

    return None


def llm_map_columns(headers: List[str], sample_rows: List[Dict[str, Any]], sheet_role: str = "MASTER ORDER SHEET") -> Dict[str, Any]:
    """
    Uses local LLM (Ollama qwen2.5:3b) to semantically map raw column headers to canonical fields.
    For Master Order Sheets: Maps order_id, sku, quantity, status, order_date (Amount excluded).
    For Payment Settlement Sheets: Maps order_id, amount, status, sku, quantity, payment_date.
    The LLM semantic response is the primary authority for header mapping.
    """
    log_stage("AGENT", f"Invoking ColumnMappingAgent (Local LLM) for {sheet_role} ({len(headers)} headers)")
    
    is_payment = "PAYMENT" in sheet_role.upper() or "SETTLEMENT" in sheet_role.upper()
    canonical_targets = (
        "order_id, amount, status, sku, quantity, payment_date" if is_payment
        else "order_id, sku, quantity, status, order_date"
    )

    llm_mappings = {}

    try:
        from app.agents.core.llm_factory import get_llm
        from app.agents.core.prompts import COLUMN_MAPPING_PROMPT
        
        llm = get_llm()

        # Truncate long string values to 35 chars to keep LLM context clean and lightweight
        sample_clean = []
        for r in sample_rows[:2]:
            clean_r = {}
            for k, v in r.items():
                if k != "id":
                    val_str = str(v)
                    clean_r[str(k)] = val_str[:35] if len(val_str) > 35 else val_str
            sample_clean.append(clean_r)
            
        sample_str = json.dumps(sample_clean, indent=2)
        headers_str = json.dumps(headers, indent=2)

        prompt_input = (
            f"{COLUMN_MAPPING_PROMPT}\n\n"
            f"Sheet Role: {sheet_role}\n"
            f"Target Canonical Fields to Map: {canonical_targets}\n\n"
            f"Exact List of Discovered Source Headers ({len(headers)} total):\n{headers_str}\n\n"
            f"Sample Data Rows Preview:\n{sample_str}\n\n"
            f"Analyze the headers and sample values above. Map EACH target canonical field to the EXACT matching column header from the list above.\n"
            f"Output a valid JSON object with key 'mappings':"
        )
        
        res = llm.invoke(prompt_input)
        res_text = getattr(res, "content", str(res))
        
        parsed = parse_json_from_llm_text(res_text)
        if parsed:
            if "mappings" in parsed and isinstance(parsed["mappings"], dict):
                llm_mappings = parsed["mappings"]
            elif isinstance(parsed, dict) and not any(k in parsed for k in ["success", "error"]):
                llm_mappings = parsed

    except Exception as e:
        log_stage("AGENT", f"LLM mapping exception: {str(e)}", level="warn")

    # Smart Fallback & Safety Filler: Ensure required fields are never omitted if present in headers
    deterministic = auto_map_payment_columns(headers) if is_payment else auto_map_order_columns(headers)
    if is_payment and "settlement_amount" in deterministic and "amount" not in deterministic:
        deterministic["amount"] = deterministic.pop("settlement_amount")

    final_mappings = {}
    
    # 1. Process LLM Mappings as Primary Source of Truth
    for c_field, info in llm_mappings.items():
        if isinstance(info, dict) and "source_column" in info:
            src_c = str(info["source_column"]).strip()
            matched = next((h for h in headers if h.lower() == src_c.lower()), src_c if src_c in headers else None)
            if matched:
                if not is_payment and c_field == "amount":
                    continue
                conf = info.get("confidence", 0.95)
                rat = info.get("rationale", f"LLM mapped canonical field '{c_field}' to '{matched}'.")
                final_mappings[c_field] = {
                    "source_column": matched,
                    "confidence": float(conf) if conf is not None else 0.95,
                    "rationale": rat
                }
        elif isinstance(info, str):
            src_c = info.strip()
            matched = next((h for h in headers if h.lower() == src_c.lower()), None)
            if matched:
                if not is_payment and c_field == "amount":
                    continue
                final_mappings[c_field] = {
                    "source_column": matched,
                    "confidence": 0.95,
                    "rationale": f"LLM mapped canonical field '{c_field}' to '{matched}'."
                }

    # 2. Fill missing canonical fields from deterministic mapper if LLM missed them
    for c_field, src_col in deterministic.items():
        if c_field not in final_mappings and src_col in headers:
            if not is_payment and c_field == "amount":
                continue
            final_mappings[c_field] = {
                "source_column": src_col,
                "confidence": 0.90,
                "rationale": f"Keyword fallback matched '{src_col}' for field '{c_field}'."
            }

    log_stage("AGENT", f"ColumnMappingAgent completed with {len(final_mappings)} canonical fields mapped")
    return {"mappings": final_mappings}


def validate_order_mapping(df_data: pd.DataFrame, mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Deterministically validates that proposed column mappings satisfy data structural constraints.
    """
    log_stage("VALIDATOR", "Starting order mapping validation")
    errors = []

    order_id_col = mapping.get("order_id")
    if not order_id_col or order_id_col not in df_data.columns:
        errors.append("Missing required 'order_id' mapping")
    else:
        series = df_data[order_id_col].dropna()
        if len(series) > 0:
            uniq_ratio = series.nunique() / len(series)
            log_stage("VALIDATOR", f"order_id ('{order_id_col}') uniqueness ratio: {round(uniq_ratio * 100, 2)}%")
            if uniq_ratio < 0.30:
                errors.append(f"Mapped order_id column '{order_id_col}' has low uniqueness ({round(uniq_ratio*100, 1)}%)")

    qty_col = mapping.get("quantity")
    if qty_col and qty_col in df_data.columns:
        valid_q = 0
        for val in df_data[qty_col].dropna().head(50):
            try:
                if int(float(str(val).strip())) > 0:
                    valid_q += 1
            except ValueError:
                pass
        qty_validity = (valid_q / min(len(df_data), 50)) * 100 if len(df_data) > 0 else 0
        log_stage("VALIDATOR", f"quantity ('{qty_col}') numeric validity: {round(qty_validity, 1)}%")

    is_valid = len(errors) == 0
    log_stage("VALIDATOR", f"Order mapping validation result: {'VALID' if is_valid else 'INVALID'}")
    return is_valid, errors


def normalize_canonical_orders(
    df_data: pd.DataFrame,
    mapping: Dict[str, str],
    source_filename: str = "",
    source_sheet: str = "",
    data_start_row: int = 2
) -> List[CanonicalOrder]:
    """
    Converts source dataframe into a list of CanonicalOrder domain models with source row traceability.
    """
    log_stage("ORDER", f"Normalizing {len(df_data)} order rows into CanonicalOrder models")
    canonical_orders: List[CanonicalOrder] = []

    order_id_col = mapping.get("order_id", df_data.columns[0])
    sku_col = mapping.get("sku")
    name_col = mapping.get("product_name")
    qty_col = mapping.get("quantity")
    status_col = mapping.get("status")
    dispatch_col = mapping.get("dispatch_date")
    order_date_col = mapping.get("order_date")

    for idx, row in df_data.iterrows():
        oid = str(row[order_id_col]).strip() if pd.notna(row[order_id_col]) else ""
        if not oid or oid.lower() in ("nan", "null", "none"):
            continue

        raw_status = str(row[status_col]).strip() if status_col and pd.notna(row[status_col]) else ""
        norm_st = normalize_status(raw_status)

        sku_val = str(row[sku_col]).strip() if sku_col and pd.notna(row[sku_col]) else ""
        name_val = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ""
        qty_val = clean_quantity(row[qty_col]) if qty_col and pd.notna(row[qty_col]) else 1
        dispatch_val = str(row[dispatch_col]).strip() if dispatch_col and pd.notna(row[dispatch_col]) else ""
        order_date_val = str(row[order_date_col]).strip() if order_date_col and pd.notna(row[order_date_col]) else ""

        c_order = CanonicalOrder(
            order_id=oid,
            sku=sku_val,
            product_name=name_val,
            quantity=qty_val,
            status=norm_st,
            dispatch_date=dispatch_val,
            order_date=order_date_val,
            source_platform="Generic",
            source_file=source_filename,
            source_sheet=source_sheet,
            source_row=data_start_row + int(idx),
            raw_data={str(k): str(v) for k, v in row.items() if pd.notna(v)}
        )
        canonical_orders.append(c_order)

    log_stage("ORDER", f"Normalized {len(canonical_orders)} CanonicalOrder records successfully")
    return canonical_orders
