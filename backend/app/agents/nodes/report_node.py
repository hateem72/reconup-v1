from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.metrics import calculate_batch_metrics
from app.core.logging import log_stage

def report_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 8: Generates final batch report metrics."""
    log_stage("NODE 8", "Executing Node 8: Report Generation")
    total_records = len(state.get("parsed_orders", []))
    rec_res = state.get("reconciliation_results", {})
    exceptions = state.get("exceptions", [])
    profit_res = state.get("financial_summary", {})
    proc_time = state.get("processing_time_ms", 120.0)

    metrics = calculate_batch_metrics(
        state.get("batch_id", "batch_demo"),
        total_records,
        rec_res,
        exceptions,
        profit_res,
        proc_time
    )

    final_report = {
        "metrics": metrics,
        "summary": profit_res.get("overall", {}),
        "skuBreakdown": profit_res.get("skuBreakdowns", {}),
        "reconciliation": rec_res,
        "exceptions": exceptions
    }

    log_stage("NODE 8", f"Generated final report: Match Rate {metrics['match_rate']}%, Profit INR {metrics['total_profit']}")

    return {
        "final_report": final_report,
        "status": "NODE_8_COMPLETED"
    }
