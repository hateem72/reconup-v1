from typing import Dict, Any, List

def calculate_batch_metrics(
    batch_id: str,
    total_records: int,
    reconciliation_result: Dict[str, Any],
    exceptions: List[Dict[str, Any]],
    processing_time_ms: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates audited reconciliation metrics:
    - total_records
    - processed_records
    - records_matched
    - match_rate
    - resolved_exceptions
    - unresolved_exceptions
    - exception_categories
    - unresolved_financial_exposure
    - processing_time_ms
    - throughput (records/sec)
    """
    matched_count = reconciliation_result.get("matchedCount", 0)
    
    # Calculate match rate strictly (matched_records / total_records)
    match_rate = (matched_count / total_records * 100.0) if total_records > 0 else 0.0

    resolved_count = 0
    unresolved_count = 0
    unresolved_impact = 0.0
    category_counts: Dict[str, int] = {}

    for exc in exceptions:
        exc_type = exc.get("exception_type", "UNKNOWN")
        category_counts[exc_type] = category_counts.get(exc_type, 0) + 1
        
        status = exc.get("status", "PENDING")
        if status in ("RESOLVED", "APPROVED"):
            resolved_count += 1
        else:
            unresolved_count += 1
            unresolved_impact += abs(float(exc.get("amount", 0.0)))

    processing_time_sec = max(processing_time_ms / 1000.0, 0.001)
    throughput = round(total_records / processing_time_sec, 2)

    return {
        "batch_id": batch_id,
        "total_records": total_records,
        "processed_records": total_records,
        "records_matched": matched_count,
        "match_rate": round(match_rate, 2),
        "resolved_exceptions": resolved_count,
        "unresolved_exceptions": unresolved_count,
        "exception_categories": category_counts,
        "unresolved_financial_exposure": round(unresolved_impact, 2),
        "processing_time_ms": round(processing_time_ms, 2),
        "throughput_records_per_sec": throughput
    }
