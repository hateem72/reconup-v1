import re
import pandas as pd
from typing import List, Dict, Any, Tuple
from app.schemas.canonical import CanonicalPayment
from app.finance.normalizer import parse_numeric_amount
from app.core.logging import log_stage

CANONICAL_PAYMENT_KEYWORDS = {
    "order_id": ["sub order no", "sub order number", "order id", "order number", "order_id", "order_no"],
    "settlement_amount": ["final settlement amount", "settlement amount", "net amount", "total payout", "amount", "payout", "settled amount"],
    "status": ["live order status", "reason for credit entry", "transaction status", "payment status", "status", "credit type"],
    "sku": ["supplier sku", "seller sku", "sku", "product sku"],
    "payment_date": ["payment date", "order date", "settlement date", "credit date", "payout date"],
    "quantity": ["quantity", "qty", "units"]
}

def auto_map_payment_columns(headers: List[str]) -> Dict[str, str]:
    """Deterministically maps source headers to canonical payment fields."""
    mapping = {}
    lower_headers = [str(h).lower().strip() for h in headers]

    for canonical_field, keywords in CANONICAL_PAYMENT_KEYWORDS.items():
        matched_col = ""
        # 1. Exact match
        for kw in keywords:
            for idx, h_lower in enumerate(lower_headers):
                if h_lower == kw:
                    matched_col = headers[idx]
                    break
            if matched_col:
                break

        # 2. Substring match
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


def validate_payment_mapping(df_data: pd.DataFrame, mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Validates payment mapping structure."""
    log_stage("VALIDATOR", "Starting payment mapping validation")
    errors = []

    order_id_col = mapping.get("order_id")
    if not order_id_col or order_id_col not in df_data.columns:
        errors.append("Missing required payment 'order_id' mapping")

    amt_col = mapping.get("settlement_amount") or mapping.get("amount")
    if not amt_col or amt_col not in df_data.columns:
        errors.append("Missing required 'settlement_amount' mapping")

    is_valid = len(errors) == 0
    log_stage("VALIDATOR", f"Payment mapping validation result: {'VALID' if is_valid else 'INVALID'}")
    return is_valid, errors


def normalize_canonical_payments(
    df_data: pd.DataFrame,
    mapping: Dict[str, str],
    source_filename: str = "",
    source_sheet: str = "",
    data_start_row: int = 2
) -> List[CanonicalPayment]:
    """
    Converts source payment dataframe into CanonicalPayment domain models.
    PRESERVES ALL MULTI-EVENT ROWS FOR THE SAME ORDER ID!
    """
    log_stage("PAYMENT", f"Normalizing {len(df_data)} payment rows into CanonicalPayment models")
    canonical_payments: List[CanonicalPayment] = []

    order_id_col = mapping.get("order_id", df_data.columns[0])
    amt_col = mapping.get("settlement_amount") or mapping.get("amount")
    status_col = mapping.get("status")
    sku_col = mapping.get("sku")
    date_col = mapping.get("payment_date")
    fee_col = mapping.get("fee_amount")
    deduction_col = mapping.get("deduction_amount")

    for idx, row in df_data.iterrows():
        oid = str(row[order_id_col]).strip() if pd.notna(row[order_id_col]) else ""
        if not oid or oid.lower() in ("nan", "null", "none"):
            continue

        raw_amt = row[amt_col] if amt_col and pd.notna(row[amt_col]) else 0.0
        amount = parse_numeric_amount(raw_amt)

        raw_status = str(row[status_col]).strip() if status_col and pd.notna(row[status_col]) else ""
        sku_val = str(row[sku_col]).strip() if sku_col and pd.notna(row[sku_col]) else ""
        date_val = str(row[date_col]).strip() if date_col and pd.notna(row[date_col]) else ""

        fee_val = parse_numeric_amount(row[fee_col]) if fee_col and pd.notna(row[fee_col]) else 0.0
        deduction_val = parse_numeric_amount(row[deduction_col]) if deduction_col and pd.notna(row[deduction_col]) else 0.0

        trx_type = "SETTLEMENT"
        if amount < 0 or deduction_val > 0 or "fee" in raw_status.lower() or "penalty" in raw_status.lower():
            trx_type = "DEDUCTION"
        elif fee_val > 0:
            trx_type = "FEE"

        c_payment = CanonicalPayment(
            transaction_id=str(row.get("Transaction ID", row.get("transaction_id", f"pmt-{idx+1}-{oid}"))).strip(),
            order_id=oid,
            sku=sku_val,
            status=raw_status,
            quantity=1,
            payment_date=date_val,
            settlement_amount=amount,
            transaction_type=trx_type,
            adjustment_reason=raw_status,
            fee_amount=fee_val,
            deduction_amount=deduction_val,
            source_platform="Generic",
            source_file=source_filename,
            source_sheet=source_sheet,
            source_row=data_start_row + int(idx),
            raw_data={str(k): str(v) for k, v in row.items() if pd.notna(v)}
        )
        canonical_payments.append(c_payment)

    log_stage("PAYMENT", f"Normalized {len(canonical_payments)} CanonicalPayment multi-event records successfully")
    return canonical_payments
