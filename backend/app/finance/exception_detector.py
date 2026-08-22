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
    Groups multiple occurrences into single actionable review items with aggregated financial exposure.
    """
    if active_rules is None:
        active_rules = []

    active_patterns = {r["pattern"].lower().strip(): r for r in active_rules if r.get("active", True)}
    grouped_unknowns: Dict[str, Dict[str, Any]] = {}

    for idx, row in enumerate(records):
        raw_status = str(row.get("Reason for Credit Entry", row.get("status", row.get("rawStatus", ""))) or "").strip()
        if not raw_status:
            continue

        raw_lower = raw_status.lower()

        # Check if already matched by active rule
        if raw_lower in active_patterns:
            continue

        # Check if matches standard known categories
        is_known = any(cat in raw_lower for cat in DEFAULT_KNOWN_CATEGORIES)
        is_unknown_keyword = any(kw in raw_lower for kw in UNKNOWN_POLICY_KEYWORDS)

        if not is_known or is_unknown_keyword:
            amt = float(row.get("amount", row.get("Payment Amount", 0)) or 0)
            order_id = str(row.get("Sub Order No", row.get("orderId", f"row-{idx}")))

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
            "order_id": sample_str,
            "exception_type": "UNKNOWN_DEDUCTION",
            "raw_status": pattern,
            "amount": round(info["total_amount"], 4),
            "description": f"Detected unknown pattern '{pattern}' affecting {info['count']} records (Total exposure: ₹{round(info['total_amount'], 2)}).",
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
    Evaluates complete batch for all exception types:
    1. Unknown deduction patterns
    2. Missing payment settlement
    3. Missing order ID in sales sheet
    """
    log_stage("EXCEPTIONS", f"Evaluating batch exceptions across {len(orders)} orders and reconciliation results")
    all_exceptions: List[Dict[str, Any]] = []

    # 1. Unknown deduction patterns
    unknown_patterns = detect_unknown_patterns(orders, active_rules)
    all_exceptions.extend(unknown_patterns)

    # 2. Missing Payment exceptions
    for item in reconciliation_results.get("missingInPayment", []):
        all_exceptions.append({
            "record_id": f"missing-pmt-{item['orderId']}",
            "order_id": item["orderId"],
            "exception_type": "MISSING_PAYMENT",
            "raw_status": item.get("orderSheetStatus", ""),
            "amount": 0.0,
            "description": f"Order {item['orderId']} was dispatched ({item.get('orderSheetStatus')}) but no payment settlement record was found.",
            "confidence": 0.95,
            "status": "PENDING",
            "requires_human": True
        })

    # 3. Missing Order exceptions
    for item in reconciliation_results.get("missingInOrder", []):
        all_exceptions.append({
            "record_id": f"missing-ord-{item['orderId']}",
            "order_id": item["orderId"],
            "exception_type": "MISSING_ORDER",
            "raw_status": item.get("paymentStatuses", ""),
            "amount": item.get("totalPayment", 0.0),
            "description": f"Payment settled for Order {item['orderId']} (₹{item.get('totalPayment')}), but order ID was missing from order sheet.",
            "confidence": 0.90,
            "status": "PENDING",
            "requires_human": True
        })

    log_stage("EXCEPTIONS", f"Batch exception evaluation finished. Total exceptions surfaced: {len(all_exceptions)}")
    return all_exceptions
