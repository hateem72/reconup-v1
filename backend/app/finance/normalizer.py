import re
from typing import Any, Tuple

# Patterns that indicate an unknown deduction/policy fee rather than a standard return/delivery
UNKNOWN_POLICY_KEYWORDS = {"assurance", "platform fee", "policy fee", "handling fee", "marketplace fee"}

def normalize_status(status: str) -> str:
    """
    Normalizes raw status strings to standardized financial categories.
    Preserves original reference implementation logic:
    - Delivered: contains 'deliver'
    - Return: contains 'return' (unless it's an unknown fee like 'return assurance fee')
    - RTO: contains 'rto'
    - Claim: contains 'compensation' or 'claim'
    - Affiliate Fees: contains 'advertisement', 'advertise', or 'affiliate'
    - Exchange: contains 'exchange'
    - Shipping: contains 'shipped' or 'shipping'
    - Cancelled: contains 'cancel'
    """
    if not status or not isinstance(status, str):
        return ""
    
    normalized = status.lower().strip()
    
    # Check if status has unknown policy keywords
    if any(keyword in normalized for keyword in UNKNOWN_POLICY_KEYWORDS):
        return status.strip()

    if "deliver" in normalized:
        return "Delivered"
    if "return" in normalized:
        # Check if it's plain Return vs compound unknown status
        if "assurance" in normalized or "fee" in normalized:
            return status.strip()
        return "Return"
    if "rto" in normalized:
        return "RTO"
    if "compensation" in normalized or "claim" in normalized:
        return "Claim"
    if "advertisement" in normalized or "advertise" in normalized or "affiliate" in normalized:
        return "Affiliate Fees"
    if "exchange" in normalized:
        return "Exchange"
    if "shipped" in normalized or "shipping" in normalized:
        return "Shipping"
    if "cancel" in normalized:
        return "Cancelled"
        
    return status.strip()


def parse_numeric_amount(amount_raw: Any, default: float = 0.0) -> float:
    """Parses raw float amount stripping currency symbols and commas."""
    if amount_raw is None or amount_raw == "":
        return default
    cleaned = re.sub(r'[₹$,\s]', '', str(amount_raw))
    try:
        return float(cleaned)
    except ValueError:
        return default


def validate_and_clean_amount(amount_raw: Any) -> Tuple[bool, float, str]:
    """
    Validates amount format, strips currency symbols (₹, $), commas, and spaces.
    Returns (is_valid, float_value, error_message).
    """
    if amount_raw is None or amount_raw == "":
        return False, 0.0, "Amount is required"
        
    cleaned = re.sub(r'[₹$,\s]', '', str(amount_raw))
    try:
        val = float(cleaned)
        return True, val, ""
    except ValueError:
        return False, 0.0, f"Invalid amount format: '{amount_raw}'"


def clean_quantity(quantity_raw: Any, default: int = 1) -> int:
    """Parses integer quantity, defaulting to specified fallback."""
    if quantity_raw is None or quantity_raw == "":
        return default
    try:
        val = int(float(str(quantity_raw).strip()))
        return val if val > 0 else default
    except (ValueError, TypeError):
        return default
