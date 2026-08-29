import re
from typing import List, Dict, Any
from app.finance.normalizer import UNKNOWN_POLICY_KEYWORDS
from app.core.logging import log_stage

DEFAULT_KNOWN_CATEGORIES = {
    "delivered", "return", "rto", "claim", "compensation", "affiliate fees",
    "advertisement", "exchange", "shipping", "cancelled"
}

def detect_unknown_patterns(records: List[Dict[str, Any]], active_rules: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Scans sales or settlement records to identify unknown/unrecognized status patterns.
    GROUPS multiple occurrences into SINGLE actionable review items with aggregated financial exposure.
    """
    if active_rules is None:
        active_rules = []

    active_patterns = {r["pattern"].lower().strip(): r for r in active_rules if r.get("active", True)}
    grouped_unknowns: Dict[str, Dict[str, Any]] = {}

    for idx, row in enumerate(records):
        if hasattr(row, "dict"):
            row_dict = row.dict()
        elif isinstance(row, dict):
            row_dict = row
        else:
            row_dict = getattr(row, "__dict__", {})

        raw_status = str(row_dict.get("status", row_dict.get("raw_status", row_dict.get("Reason for Credit Entry", ""))) or "").strip()
        if not raw_status or raw_status.lower() in ("nan", "null", "none"):
            continue

        raw_lower = raw_status.lower()

        # Check if already matched by active rule
        if raw_lower in active_patterns:
            continue

        # Check if matches standard known categories
        is_known = any(cat in raw_lower for cat in DEFAULT_KNOWN_CATEGORIES)
        is_unknown_keyword = any(kw in raw_lower for kw in UNKNOWN_POLICY_KEYWORDS)

        if not is_known or is_unknown_keyword:
            amt = float(row_dict.get("settlement_amount", row_dict.get("amount", row_dict.get("Payment Amount", 0))) or 0)
            order_id = str(row_dict.get("order_id", row_dict.get("Sub Order No", row_dict.get("orderId", f"row-{idx}"))))

            if raw_status not in grouped_unknowns:
                grouped_unknowns[raw_status] = {
                    "raw_status": raw_status,
                    "count": 0,
                    "total_amount": 0.0,
                    "sample_orders": []
                }

            grouped_unknowns[raw_status]["count"] += 1
            grouped_unknowns[raw_status]["total_amount"] += amt
            if len(grouped_unknowns[raw_status]["sample_orders"]) < 5:
                grouped_unknowns[raw_status]["sample_orders"].append(order_id)

    exceptions = []
    for pattern, info in grouped_unknowns.items():
        sample_str = ", ".join(info["sample_orders"])
        exceptions.append({
            "record_id": f"pattern-{pattern.lower().replace(' ', '-')}",
            "order_id": f"{info['count']} Orders (Samples: {sample_str})",
            "exception_type": "UNKNOWN_DEDUCTION",
            "raw_status": pattern,
            "amount": round(info["total_amount"], 4),
            "description": f"Detected unknown pattern '{pattern}' across {info['count']} order rows (Aggregated financial impact: ₹{round(info['total_amount'], 2)}).",
            "confidence": 0.85,
            "status": "PENDING",
            "requires_human": True,
            "occurrences": info["count"]
        })

    return exceptions


def evaluate_batch_exceptions(
    orders: List[Dict[str, Any]],
    reconciliation_results: Dict[str, Any],
    active_rules: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates complete batch for high-level governance exception cards.
    NEVER SURFACES 1,900 INDIVIDUAL ROWS.
    Aggregates missing payments, missing orders, and unknown patterns into 3-5 concise governance items.
    """
    log_stage("EXCEPTIONS", f"Evaluating batch exceptions across {len(orders)} orders")
    all_exceptions: List[Dict[str, Any]] = []

    # 1. Unknown deduction patterns (Grouped by unique pattern text)
    unknown_patterns = detect_unknown_patterns(orders, active_rules)
    all_exceptions.extend(unknown_patterns)

    # 2. Aggregated Missing Payment Exception Card (1 Summary Card for ALL missing payments)
    missing_payments = reconciliation_results.get("missingInPayment", [])
    if missing_payments:
        cnt = len(missing_payments)
        sample_oids = [m["orderId"] for m in missing_payments[:5]]
        sample_str = ", ".join(sample_oids)
        all_exceptions.append({
            "record_id": "summary-missing-payments",
            "order_id": f"{cnt} Orders Missing Payment (Samples: {sample_str})",
            "exception_type": "MISSING_PAYMENT_SUMMARY",
            "raw_status": "Missing Payment Settlement",
            "amount": 0.0,
            "description": f"{cnt} orders in the Order Sheet have no corresponding payment settlement records in uploaded payment sheets.",
            "confidence": 0.95,
            "status": "PENDING",
            "requires_human": True,
            "occurrences": cnt
        })

    # 3. Aggregated Missing Order Exception Card (1 Summary Card for extra payment settlements)
    missing_orders = reconciliation_results.get("missingInOrder", [])
    if missing_orders:
        cnt = len(missing_orders)
        tot_settlement = sum(float(m.get("totalPayment", 0)) for m in missing_orders)
        sample_oids = [m["orderId"] for m in missing_orders[:5]]
        sample_str = ", ".join(sample_oids)
        all_exceptions.append({
            "record_id": "summary-missing-orders",
            "order_id": f"{cnt} Historical Settlements (Samples: {sample_str})",
            "exception_type": "HISTORICAL_PAYMENTS_SUMMARY",
            "raw_status": "Historical Payment Settlement",
            "amount": round(tot_settlement, 4),
            "description": f"{cnt} payment settlement entries (Total ₹{round(tot_settlement, 2)}) reference Order IDs not present in current month Order Sheet (likely previous month settlements).",
            "confidence": 0.90,
            "status": "PENDING",
            "requires_human": False,
            "occurrences": cnt
        })

    log_stage("EXCEPTIONS", f"Governance evaluation finished. Surface {len(all_exceptions)} concise high-level cards (no row clutter)")
    return all_exceptions
