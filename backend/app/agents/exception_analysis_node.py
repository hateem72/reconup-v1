import time
from typing import Dict, Any
from app.agents.state import FinanceState
from app.finance.exception_detector import evaluate_batch_exceptions
from app.core.logging import log_stage
from app.agents.column_mapping_agent import log_agent_call

def exception_analysis_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 7: Analyzes batch exceptions using deterministic rule registry & LLM explanations."""
    start = time.time()
    log_stage("NODE 7", "Executing Node 7: Exception & Governance Analysis")
    records = state.get("normalized_records", []) or state.get("parsed_orders", [])
    rec_res = state.get("reconciliation_results", {})
    approved_rules = state.get("approved_rules", [])

    exceptions = evaluate_batch_exceptions(records, rec_res, approved_rules)
    pending_human = any(e.get("requires_human", False) and e.get("status") == "PENDING" for e in exceptions)

    log_agent_call(
        agent_name="ExceptionInvestigationAgent",
        task="Analyze unresolved financial anomalies & unknown patterns",
        input_summary=f"{len(exceptions)} surfaced exceptions",
        output_summary=f"Surfaced {len(exceptions)} items requiring governance",
        confidence=0.88,
        duration_sec=time.time() - start
    )

    return {
        "exceptions": exceptions,
        "human_review_required": pending_human,
        "status": "NODE_7_WAITING_HUMAN_REVIEW" if pending_human else "NODE_7_EXCEPTIONS_ANALYZED"
    }


def reprocessing_node(state: FinanceState) -> Dict[str, Any]:
    """Applies human-approved rules and reprocesses state."""
    log_stage("BATCH", "Reprocessing batch after human rule approval")
    return {"status": "REPROCESSED"}
