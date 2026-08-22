from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.core.logging import log_stage

def financial_calculation_node(state: FinanceState) -> Dict[str, Any]:
    """NODE 6: Executes deterministic profit/loss calculations."""
    log_stage("NODE 6", "Executing Node 6: Profit/Loss Calculation")
    records = state.get("normalized_records", []) or state.get("parsed_orders", [])
    grouped = group_by_sku(records)
    profit_res = calculate_overall_profit(grouped)
    return {
        "financial_summary": profit_res,
        "status": "NODE_6_CALCULATED"
    }
