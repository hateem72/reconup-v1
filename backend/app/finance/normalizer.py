import re
import json
import pandas as pd
from typing import List, Dict, Any, Tuple
from app.schemas.canonical import CanonicalOrder, CanonicalPayment
from app.core.logging import log_stage

CANONICAL_STATUS_MAP = {
    "DELIVERED": "Delivered",
    "DELIVERED_TO_CUSTOMER": "Delivered",
    "COMPLETED": "Delivered",
    "SUCCESSFUL": "Delivered",
    "RETURN": "Return",
    "CUSTOMER_RETURN": "Return",
    "RETURNED": "Return",
    "RETURN_INITIATED": "Return_Initiated",
    "RETURN_IN_TRANSIT": "Return_Initiated",
    "RTO": "RTO",
    "RETURN_TO_ORIGIN": "RTO",
    "RTO_COMPLETE": "RTO",
    "RTO_IN_TRANSIT": "RTO",
    "CANCELLED": "Cancelled",
    "CANCELED": "Cancelled",
    "SHIPPED": "Shipped",
    "DISPATCHED": "Shipped",
    "IN_TRANSIT": "Shipped",
    "ON_THE_WAY": "Shipped",
    "CLAIM": "Claim",
    "COMPENSATION_CLAIM": "Claim",
    "COMPENSATION": "Compensation",
    "LOST_COMPENSATION": "Compensation",
    "EXCHANGE": "Exchange",
    "REPLACEMENT": "Exchange",
    "DOOR_STEP_EXCHANGED": "Exchange"
}

UNKNOWN_POLICY_KEYWORDS = ["return assurance", "assurance fee", "recovery fee", "other support service", "penalty charge"]

def normalize_status(raw_status: Any) -> str:
    """Deterministically normalizes raw status strings to canonical categories."""
    if not raw_status or pd.isna(raw_status):
        return "Delivered"

    clean_str = str(raw_status).strip().upper()
    
    if clean_str in CANONICAL_STATUS_MAP:
        return CANONICAL_STATUS_MAP[clean_str]

    for key, val in CANONICAL_STATUS_MAP.items():
        if key in clean_str:
            return val

    return "Delivered"


def llm_normalize_statuses(raw_statuses: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Uses Local LLM (Ollama qwen2.5:3b) to semantically categorize raw status strings
    into standardized canonical categories (Delivered, Return, RTO, Cancelled, Shipped, Return_Initiated, Claim, Compensation, Exchange, Deduction).
    Fallback to deterministic normalize_status.
    """
    unique_statuses = sorted(list(set([str(s).strip() for s in raw_statuses if str(s).strip()])))
    if not unique_statuses:
        return {}

    log_stage("AGENT", f"Invoking StatusNormalizationAgent (Local LLM) for {len(unique_statuses)} unique raw statuses")
    
    try:
        from app.agents.core.llm_factory import get_llm
        from app.agents.core.prompts import STATUS_NORMALIZATION_PROMPT
        
        llm = get_llm()
        prompt_input = (
            f"{STATUS_NORMALIZATION_PROMPT}\n\n"
            f"Raw Status Strings to Categorize:\n{json.dumps(unique_statuses, indent=2)}\n\n"
            f"Respond with valid JSON mapping dictionary:"
        )
        
        res = llm.invoke(prompt_input)
        res_text = getattr(res, "content", str(res))
        
        json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            mappings = parsed.get("status_mappings", parsed)
            if isinstance(mappings, dict) and len(mappings) > 0:
                log_stage("AGENT", f"StatusNormalizationAgent (LLM) categorized {len(mappings)} raw status strings")
                return mappings
    except Exception as e:
        log_stage("AGENT", f"LLM status normalization fallback to deterministic: {str(e)}", level="warn")

    # Fallback to deterministic regex normalization
    fallback = {}
    for st in unique_statuses:
        norm_c = normalize_status(st)
        fallback[st] = {
            "canonical_category": norm_c,
            "confidence": 1.0
        }
    return fallback


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
    """Validates amount format, strips currency symbols (₹, $), commas, and spaces."""
    if amount_raw is None or amount_raw == "":
        return False, 0.0, "Amount is empty"

    cleaned = re.sub(r'[₹$,\s]', '', str(amount_raw))
    try:
        val = float(cleaned)
        return True, val, ""
    except ValueError:
        return False, 0.0, f"Invalid numeric amount format: '{amount_raw}'"


def clean_quantity(qty_raw: Any, default: int = 1) -> int:
    """Parses integer quantity safely."""
    if qty_raw is None or qty_raw == "":
        return default
    try:
        val = int(float(str(qty_raw).strip()))
        return val if val > 0 else default
    except (ValueError, TypeError):
        return default
