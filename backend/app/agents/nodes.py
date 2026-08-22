"""
Central Agentic Node Registry

Imports and re-exports all modular AI agent & graph pipeline node execution functions:
- Node 1: Ingest & Exact Header Profiling (ingest_node)
- Node 1.5: AI Sheet Relevance Agent (SheetRelevanceAgent / sheet_filtering_node)
- Node 2: Column Mapping Agent & Structural Guardrails (ColumnMappingAgent / validation_node)
- Node 3: Status Normalization Agent & Canonical Normalization (StatusNormalizationAgent / normalization_node)
- Node 4: Pattern Detection Agent & Status Integrity Repair (pattern_detection_node)
- Node 5: Deterministic Order-Payment Reconciliation Engine (ReconciliationEngine / reconciliation_node)
- Node 6: Financial P&L Calculation Node (financial_calculation_node)
- Node 7: Exception Investigation Agent & Reprocessing (ExceptionInvestigationAgent / exception_analysis_node, reprocessing_node)
- Node 8: Report Generation Node (report_node)
"""

from app.agents.ingest_node import ingest_node
from app.agents.sheet_relevance_agent import SheetRelevanceAgent
from app.agents.column_mapping_agent import validation_node, log_agent_call
from app.agents.status_normalization_agent import normalization_node
from app.agents.pattern_detection_agent import pattern_detection_node
from app.agents.reconciliation_node import reconciliation_node
from app.agents.financial_calculation_node import financial_calculation_node
from app.agents.exception_analysis_node import exception_analysis_node, reprocessing_node
from app.agents.report_node import report_node

def sheet_filtering_node(state):
    """NODE 1.5: Delegates to dedicated SheetRelevanceAgent to evaluate sub-tabs."""
    agent = SheetRelevanceAgent()
    raw_datasets = state.get("raw_datasets", [])
    result = agent.evaluate_sheet_relevance(raw_datasets)
    return {
        "raw_datasets": result.get("retained_datasets", []),
        "dropped_datasets": result.get("dropped_datasets", []),
        "status": "NODE_RELEVANCE_COMPLETED"
    }

__all__ = [
    "log_agent_call",
    "ingest_node",
    "sheet_filtering_node",
    "validation_node",
    "normalization_node",
    "pattern_detection_node",
    "reconciliation_node",
    "financial_calculation_node",
    "exception_analysis_node",
    "reprocessing_node",
    "report_node"
]
