import re
import json
from typing import Any, Tuple, List, Dict
from app.core.logging import log_stage

# Patterns that indicate an unknown deduction/policy fee rather than a standard return/delivery
UNKNOWN_POLICY_KEYWORDS = {"assurance", "platform fee", "policy fee", "handling fee", "marketplace fee"}

def normalize_status(status: str) -> str:
    """
    Normalizes raw status strings to standardized financial categories.
    - Delivered: contains 'deliver'
    - Return: contains 'return' (unless it's an unknown fee like 'return assurance fee')
    - RTO: contains 'rto'
    - Claim: contains 'compensation' or 'claim'
    - Affiliate Fees: contains 'advertisement', 'advertise', or 'affiliate'
    - Exchange: contains 'exchange'
    - Shipping / Shipped: contains 'shipped' or 'shipping'
    - Cancelled: contains 'cancel'
    """
    if not status or not isinstance(status, str):
        return ""
    
    normalized = status.lower().strip()
    
    if any(keyword in normalized for keyword in UNKNOWN_POLICY_KEYWORDS):
        return status.strip()

    if "deliver" in normalized:
        return "Delivered"
    if "return" in normalized:
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
    if "shipped" in normalized or "shipping" in normalized or "dispatch" in normalized:
        return "Shipped"
    if "cancel" in normalized:
        return "Cancelled"
        
    return status.strip()


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
            if "status_mappings" in parsed and isinstance(parsed["status_mappings"], dict):
                log_stage("AGENT", f"StatusNormalizationAgent (LLM) categorized {len(parsed['status_mappings'])} raw status strings")
                return parsed["status_mappings"]
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
