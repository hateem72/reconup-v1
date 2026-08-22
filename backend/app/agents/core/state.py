from typing import TypedDict, List, Dict, Any, Optional

class FinanceState(TypedDict, total=False):
    batch_id: str
    file_ids: List[str]
    source_filename: str
    parsed_orders: List[Dict[str, Any]]
    parsed_payments: List[Dict[str, Any]]
    normalized_records: List[Dict[str, Any]]
    validation_errors: List[Dict[str, Any]]
    unknown_patterns: List[Dict[str, Any]]
    reconciliation_results: Dict[str, Any]
    exceptions: List[Dict[str, Any]]
    financial_summary: Dict[str, Any]
    match_rate: float
    processing_time_ms: float
    human_review_required: bool
    approved_rules: List[Dict[str, Any]]
    final_report: Dict[str, Any]
    status: str
