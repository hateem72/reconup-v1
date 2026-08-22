from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.core.state import FinanceState
from app.agents.nodes import (
    ingest_node,
    sheet_filtering_node,
    validation_node,
    normalization_node,
    pattern_detection_node,
    reconciliation_node,
    financial_calculation_node,
    exception_analysis_node,
    reprocessing_node,
    report_node
)

def route_after_exception_analysis(state: FinanceState) -> str:
    """Routes to human review if unknown/ambiguous exceptions exist, else directly to report."""
    if state.get("human_review_required", False):
        return "WAITING_HUMAN_REVIEW"
    return "generate_report"

def build_finance_graph():
    """
    Constructs the LangGraph state machine workflow for Finance Controller.
    """
    workflow = StateGraph(FinanceState)

    # Add Nodes
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("filter_sheets", sheet_filtering_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("normalize", normalization_node)
    workflow.add_node("detect", pattern_detection_node)
    workflow.add_node("reconcile", reconciliation_node)
    workflow.add_node("calculate", financial_calculation_node)
    workflow.add_node("exceptions", exception_analysis_node)
    workflow.add_node("reprocess", reprocessing_node)
    workflow.add_node("generate_report", report_node)

    # Define Edges
    workflow.set_entry_point("ingest")
    workflow.add_edge("ingest", "filter_sheets")
    workflow.add_edge("filter_sheets", "validate")
    workflow.add_edge("validate", "normalize")
    workflow.add_edge("normalize", "detect")
    workflow.add_edge("detect", "reconcile")
    workflow.add_edge("reconcile", "calculate")
    workflow.add_edge("calculate", "exceptions")

    workflow.add_conditional_edges(
        "exceptions",
        route_after_exception_analysis,
        {
            "WAITING_HUMAN_REVIEW": "reprocess",
            "generate_report": "generate_report"
        }
    )

    workflow.add_edge("reprocess", "generate_report")
    workflow.add_edge("generate_report", END)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
