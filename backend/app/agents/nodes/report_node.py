from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.metrics import calculate_batch_metrics
from app.core.logging import log_stage

def report_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 7 / 8: Generates final batch report metrics."""
    log_stage("NODE 8", "Executing Node 8: Executive Report Generation")
    total_records = len(state.get("parsed_orders", []))
    rec_res = state.get("reconciliation_results", {})
    exceptions = state.get("exceptions", [])
    proc_time = state.get("processing_time_ms", 120.0)

    metrics = calculate_batch_metrics(
        batch_id=state.get("batch_id", "batch_demo"),
        total_records=total_records,
        reconciliation_result=rec_res,
        exceptions=exceptions,
        processing_time_ms=proc_time
    )

    final_report = {
        "metrics": metrics,
        "reconciliation": rec_res,
        "exceptions": exceptions
    }

    log_stage("NODE 8", f"Generated final report: Match Rate {metrics['match_rate']}%, Exposure INR {metrics['unresolved_financial_exposure']}")

    return {
        "final_report": final_report,
        "status": "NODE_8_COMPLETED"
    }
