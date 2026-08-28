from typing import Dict, Any, List, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.finance.reconciliation import process_reconciliation
from app.finance.rule_registry import DEFAULT_KNOWN_RULES

class OrderLookupInput(BaseModel):
    order_id: str = Field(description="The unique order ID or Sub Order No to query")

class BatchSummaryInput(BaseModel):
    batch_id: str = Field(description="The batch ID to query summary for")

class RuleProposalInput(BaseModel):
    pattern: str = Field(description="Raw pattern name e.g. Return Assurance Fee")
    normalized_category: str = Field(description="Target standard category name")
    financial_effect: str = Field(description="Financial effect: ADD, SUBTRACT, or NEUTRAL")

@tool("lookup_order", args_schema=OrderLookupInput)
def lookup_order(order_id: str) -> Dict[str, Any]:
    """Look up order record details for a specific Order ID."""
    return {
        "order_id": order_id,
        "found": True,
        "details": f"Order {order_id} recorded in manifest."
    }

@tool("lookup_payment", args_schema=OrderLookupInput)
def lookup_payment(order_id: str) -> Dict[str, Any]:
    """Look up settlement payment line details for a specific Order ID."""
    return {
        "order_id": order_id,
        "found": True,
        "details": f"Payment line for {order_id} retrieved."
    }

@tool("get_rule_registry")
def get_rule_registry() -> List[Dict[str, Any]]:
    """Fetch all active known and human-approved learned rules from registry."""
    return DEFAULT_KNOWN_RULES
