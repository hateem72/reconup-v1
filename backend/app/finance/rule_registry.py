from typing import List, Dict, Any, Optional

DEFAULT_KNOWN_RULES = [
    {
        "pattern": "delivered",
        "normalized_category": "Delivered",
        "financial_effect": "ADD",
        "amount_behavior": "REVENUE",
        "applies_to": "DELIVERED",
        "confidence": 1.0,
        "created_by": "system",
        "active": True
    },
    {
        "pattern": "return",
        "normalized_category": "Return",
        "financial_effect": "SUBTRACT",
        "amount_behavior": "PENALTY",
        "applies_to": "RETURN",
        "confidence": 1.0,
        "created_by": "system",
        "active": True
    },
    {
        "pattern": "rto",
        "normalized_category": "RTO",
        "financial_effect": "NEUTRAL",
        "amount_behavior": "ZERO_AMOUNT",
        "applies_to": "RTO",
        "confidence": 1.0,
        "created_by": "system",
        "active": True
    },
    {
        "pattern": "claim",
        "normalized_category": "Claim",
        "financial_effect": "ADD",
        "amount_behavior": "CREDIT",
        "applies_to": "CLAIM",
        "confidence": 1.0,
        "created_by": "system",
        "active": True
    },
    {
        "pattern": "affiliate",
        "normalized_category": "Affiliate Fees",
        "financial_effect": "SUBTRACT",
        "amount_behavior": "DEDUCTION",
        "applies_to": "ADVERTISEMENT",
        "confidence": 1.0,
        "created_by": "system",
        "active": True
    }
]

class RuleRegistryManager:
    def __init__(self, initial_rules: Optional[List[Dict[str, Any]]] = None):
        self.rules: List[Dict[str, Any]] = list(initial_rules) if initial_rules else list(DEFAULT_KNOWN_RULES)

    def add_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        pattern = str(rule.get("pattern") or "").lower().strip()
        new_rule = {
            "pattern": pattern,
            "normalized_category": rule.get("normalized_category", pattern.title()),
            "financial_effect": rule.get("financial_effect", "SUBTRACT"),
            "amount_behavior": rule.get("amount_behavior", "DEDUCTION"),
            "applies_to": rule.get("applies_to", "ALL"),
            "confidence": float(rule.get("confidence", 1.0)),
            "created_by": rule.get("created_by", "human"),
            "active": True
        }
        
        # Deactivate existing rule with same pattern if exists
        for existing in self.rules:
            if existing.get("pattern", "").lower() == pattern:
                existing["active"] = False

        self.rules.append(new_rule)
        return new_rule

    def match_rule(self, raw_status: str) -> Optional[Dict[str, Any]]:
        if not raw_status:
            return None
        target = raw_status.lower().strip()
        for rule in self.rules:
            if rule.get("active", True) and rule.get("pattern", "").lower() in target:
                return rule
        return None

    def get_active_rules(self) -> List[Dict[str, Any]]:
        return [r for r in self.rules if r.get("active", True)]
