import re
from typing import List, Dict, Any
from app.finance.normalizer import validate_and_clean_amount

KNOWN_VALID_STATUSES = {
    "delivered", "return", "rto", "compensation", "advertisement",
    "claim", "affiliate fees", "exchange", "shipped", "cancelled",
    "shipping", "canceled"
}

def validate_sales_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates sales/settlement data for missing or invalid values.
    Returns dict containing {isValid, errors, warnings, missingData}.
    """
    errors: List[str] = []
    warnings: List[str] = []
    missing_data: List[Dict[str, Any]] = []

    if not data:
        errors.append("No data to validate")
        return {
            "isValid": False,
            "errors": errors,
            "warnings": warnings,
            "missingData": missing_data
        }

    for index, row in enumerate(data):
        row_errors: List[str] = []
        row_num = row.get("rowNumber", index + 1)
        sku_id = str(row.get("skuId", "") or "").strip()
        status_raw = str(row.get("status", "") or "").strip()
        amount_raw = row.get("amount")
        quantity_raw = row.get("quantity")

        # 1. Missing SKU ID
        if not sku_id:
            row_errors.append("Missing SKU ID")

        # 2. Missing or unknown Status
        if not status_raw:
            row_errors.append("Missing Status")
        else:
            status_lower = status_raw.lower()
            if not any(valid_st in status_lower for valid_st in KNOWN_VALID_STATUSES):
                row_errors.append(
                    f"Invalid status: '{status_raw}'. Expected standard status like Delivered, Return, RTO, Claim, etc."
                )

        # 3. Missing or invalid Amount
        if amount_raw is None or str(amount_raw).strip() == "":
            row_errors.append("Missing Amount")
        else:
            is_valid_amt, parsed_amt, _ = validate_and_clean_amount(amount_raw)
            if not is_valid_amt:
                row_errors.append(f"Invalid amount: '{amount_raw}'")

        # 4. Missing or invalid Quantity
        if quantity_raw is None or str(quantity_raw).strip() == "":
            row_errors.append("Missing Quantity")
        else:
            try:
                qty_val = int(float(str(quantity_raw).strip()))
                if qty_val <= 0:
                    row_errors.append(f"Invalid quantity: '{quantity_raw}'. Must be > 0")
            except (ValueError, TypeError):
                row_errors.append(f"Invalid quantity format: '{quantity_raw}'")

        if row_errors:
            missing_data.push({
                "rowNumber": row_num,
                "rowId": row.get("id", f"row-{index}"),
                "errors": row_errors,
                "data": row
            } if hasattr(missing_data, 'push') else None)
            # In python, list.append:
            missing_data.append({
                "rowNumber": row_num,
                "rowId": row.get("id", f"row-{index}"),
                "errors": row_errors,
                "data": row
            })

        # Generate business rule warnings
        if status_raw and "deliver" in status_raw.lower():
            is_valid_amt, parsed_amt, _ = validate_and_clean_amount(amount_raw)
            if is_valid_amt and parsed_amt < 0:
                warnings.append(f"Row {row_num}: Delivered item with negative amount ({parsed_amt})")

        if status_raw and "return" in status_raw.lower():
            is_valid_amt, parsed_amt, _ = validate_and_clean_amount(amount_raw)
            if is_valid_amt and parsed_amt > 0:
                warnings.append(f"Row {row_num}: Return item with positive amount ({parsed_amt})")

        if status_raw and "rto" in status_raw.lower():
            is_valid_amt, parsed_amt, _ = validate_and_clean_amount(amount_raw)
            if is_valid_amt and parsed_amt != 0:
                warnings.append(f"Row {row_num}: RTO item should typically have zero amount ({parsed_amt})")

    return {
        "isValid": len(missing_data) == 0,
        "errors": errors,
        "warnings": warnings,
        "missingData": missing_data
    }
