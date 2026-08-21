from typing import List, Dict, Any
from app.finance.normalizer import normalize_status, validate_and_clean_amount

KNOWN_STATUS_CATEGORIES = {
    "Delivered", "Return", "RTO", "Claim",
    "Affiliate Fees", "Exchange", "Shipping", "Cancelled"
}

def detect_unknown_patterns(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Groups and detects unknown status/deduction patterns across records.
    Example: 'Return Assurance Fee' detected across 37 records -> grouped into 1 review item.
    """
    pattern_groups: Dict[str, Dict[str, Any]] = {}

    for index, record in enumerate(records):
        raw_status = str(record.get("status") or "").strip()
        if not raw_status:
            continue

        normalized = normalize_status(raw_status)
        
        # If the normalized status matches known categories, skip unknown pattern detection
        if normalized in KNOWN_STATUS_CATEGORIES:
            continue

        pattern_key = raw_status.lower()
        _, amt, _ = validate_and_clean_amount(record.get("amount", 0))
        order_id = str(record.get("orderId", record.get("skuId", f"REC-{index}")))

        if pattern_key not in pattern_groups:
            pattern_groups[pattern_key] = {
                "pattern": raw_status,
                "occurrences": 0,
                "total_impact": 0.0,
                "sample_orders": [],
                "candidate_interpretation": f"Unrecognized category '{raw_status}'. AI review recommended.",
                "confidence": 0.70,
                "requires_human_review": True
            }

        pattern_groups[pattern_key]["occurrences"] += 1
        pattern_groups[pattern_key]["total_impact"] += amt
        if len(pattern_groups[pattern_key]["sample_orders"]) < 5:
            pattern_groups[pattern_key]["sample_orders"].append(order_id)

    # Convert dictionary to list and round financial impact
    result = []
    for pg in pattern_groups.values():
        pg["total_impact"] = round(pg["total_impact"], 4)
        result.append(pg)

    return result


def evaluate_batch_exceptions(
    records: List[Dict[str, Any]],
    reconciliation_data: Dict[str, Any],
    learned_rules: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates individual exceptions (missing payment, missing order, amount mismatch, unknown pattern).
    Checks if learned rules match any unknown status.
    """
    if learned_rules is None:
        learned_rules = []

    active_rule_patterns = {r.get("pattern", "").lower(): r for r in learned_rules if r.get("active", True)}
    exceptions: List[Dict[str, Any]] = []

    # 1. Reconciliation Missing Payments
    for item in reconciliation_data.get("missingInPayment", []):
        exceptions.append({
            "record_id": item["orderId"],
            "order_id": item["orderId"],
            "exception_type": "MISSING_PAYMENT",
            "raw_status": item.get("orderSheetStatus", ""),
            "amount": 0.0,
            "description": f"Order {item['orderId']} exists in order log but missing settlement payment record.",
            "confidence": 0.95,
            "status": "PENDING",
            "requires_human": False
        })

    # 2. Reconciliation Missing Orders
    for item in reconciliation_data.get("missingInOrder", []):
        exceptions.append({
            "record_id": item["orderId"],
            "order_id": item["orderId"],
            "exception_type": "MISSING_ORDER",
            "raw_status": item.get("paymentStatuses", ""),
            "amount": item.get("totalPayment", 0.0),
            "description": f"Payment recorded for order {item['orderId']} but missing in master order manifest.",
            "confidence": 0.90,
            "status": "PENDING",
            "requires_human": False
        })

    # 3. Unknown Statuses
    unknown_patterns = detect_unknown_patterns(records)
    for up in unknown_patterns:
        pattern_lower = up["pattern"].lower()
        if pattern_lower in active_rule_patterns:
            rule = active_rule_patterns[pattern_lower]
            # Resolved automatically by learned rule!
            exceptions.append({
                "record_id": f"pattern-{pattern_lower}",
                "order_id": "N/A",
                "exception_type": "RESOLVED_BY_RULE",
                "raw_status": up["pattern"],
                "amount": up["total_impact"],
                "description": f"Pattern '{up['pattern']}' automatically resolved by learned rule: {rule['normalized_category']}",
                "confidence": 1.0,
                "status": "RESOLVED",
                "requires_human": False
            })
        else:
            exceptions.append({
                "record_id": f"pattern-{pattern_lower}",
                "order_id": "N/A",
                "exception_type": "UNKNOWN_DEDUCTION",
                "raw_status": up["pattern"],
                "amount": up["total_impact"],
                "description": f"Unknown financial status '{up['pattern']}' detected across {up['occurrences']} records with ₹{up['total_impact']} total impact.",
                "confidence": up["confidence"],
                "status": "PENDING",
                "requires_human": True
            })

    return exceptions
