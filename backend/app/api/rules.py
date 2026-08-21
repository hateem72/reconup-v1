from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository

router = APIRouter()

class CreateRuleRequest(BaseModel):
    pattern: str
    normalized_category: str
    financial_effect: str = "SUBTRACT" # ADD, SUBTRACT, NEUTRAL
    amount_behavior: str = "DEDUCTION"

@router.get("/rules")
def get_rule_registry(db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    rules = repo.get_all_rules(active_only=False)
    return {
        "total_rules": len(rules),
        "rules": [
            {
                "id": r.id,
                "pattern": r.pattern,
                "normalized_category": r.normalized_category,
                "financial_effect": r.financial_effect,
                "amount_behavior": r.amount_behavior,
                "confidence": r.confidence,
                "created_by": r.created_by,
                "created_at": r.created_at,
                "active": r.active
            }
            for r in rules
        ]
    }

@router.post("/rules")
def create_rule(req: CreateRuleRequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    rule = repo.create_rule(
        pattern=req.pattern,
        category=req.normalized_category,
        effect=req.financial_effect,
        behavior=req.amount_behavior,
        created_by="human"
    )
    return {
        "success": True,
        "rule": {
            "id": rule.id,
            "pattern": rule.pattern,
            "normalized_category": rule.normalized_category,
            "financial_effect": rule.financial_effect
        }
    }
