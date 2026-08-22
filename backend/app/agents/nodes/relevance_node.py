from typing import Dict, Any
from app.agents.state import FinanceState
from app.agents.sheet_relevance_agent import SheetRelevanceAgent

def sheet_filtering_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 1.5: Delegates to dedicated SheetRelevanceAgent to evaluate sub-tabs."""
    agent = SheetRelevanceAgent()
    raw_datasets = state.get("raw_datasets", [])
    result = agent.evaluate_sheet_relevance(raw_datasets)
    return {
        "raw_datasets": result.get("retained_datasets", []),
        "dropped_datasets": result.get("dropped_datasets", []),
        "status": "NODE_RELEVANCE_COMPLETED"
    }
