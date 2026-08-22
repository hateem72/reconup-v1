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

from app.agents.nodes.ingest_node import ingest_node
from app.agents.nodes.relevance_node import sheet_filtering_node
from app.agents.specialized.sheet_relevance_agent import SheetRelevanceAgent
from app.agents.specialized.column_mapping_agent import validation_node, log_agent_call
from app.agents.specialized.status_normalization_agent import normalization_node
from app.agents.specialized.pattern_detection_agent import pattern_detection_node
from app.agents.nodes.reconciliation_node import reconciliation_node
from app.agents.nodes.financial_calculation_node import financial_calculation_node
from app.agents.nodes.exception_analysis_node import exception_analysis_node, reprocessing_node
from app.agents.nodes.report_node import report_node

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
