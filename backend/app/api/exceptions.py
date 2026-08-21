from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository

router = APIRouter()

class ExceptionDecisionRequest(BaseModel):
    decision: str # APPROVE, REJECT, EDIT_RULE
    note: Optional[str] = ""
    target_category: Optional[str] = ""
    financial_effect: Optional[str] = "SUBTRACT"

@router.get("/batches/{batch_id}/exceptions")
def get_batch_exceptions(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    exceptions = repo.get_exceptions(batch_id)
    return {
        "batch_id": batch_id,
        "total_exceptions": len(exceptions),
        "pending_count": len([e for e in exceptions if e.status == "PENDING"]),
        "exceptions": [
            {
                "id": e.id,
                "record_id": e.record_id,
                "order_id": e.order_id,
                "exception_type": e.exception_type,
                "raw_status": e.raw_status,
                "amount": e.amount,
                "description": e.description,
                "agent_analysis": e.agent_analysis,
                "confidence": e.confidence,
                "status": e.status,
                "human_decision": e.human_decision,
                "human_note": e.human_note,
                "created_at": e.created_at,
                "resolved_at": e.resolved_at
            }
            for e in exceptions
        ]
    }

@router.post("/exceptions/{id}/approve")
def approve_exception(id: int, req: ExceptionDecisionRequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    exc = repo.resolve_exception(id, decision="APPROVE", note=req.note or "Approved by human operator")
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")

    # If exception was an unknown pattern, persist learned rule!
    if exc.raw_status:
        category = req.target_category or exc.raw_status.title()
        effect = req.financial_effect or "SUBTRACT"
        repo.create_rule(pattern=exc.raw_status, category=category, effect=effect, created_by="human")

    # Check if remaining pending exceptions exist for batch
    pending = repo.get_exceptions(exc.batch_id, status_filter="PENDING")
    if not pending:
        repo.update_batch_status(exc.batch_id, "COMPLETED")

    return {
        "success": True,
        "exception_id": exc.id,
        "status": exc.status,
        "rule_created": exc.raw_status,
        "message": f"Rule '{exc.raw_status}' learned and persisted into database registry."
    }

@router.post("/exceptions/{id}/reject")
def reject_exception(id: int, req: ExceptionDecisionRequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    exc = repo.resolve_exception(id, decision="REJECT", note=req.note or "Rejected by human operator")
    if not exc:
        raise HTTPException(status_code=404, detail="Exception not found")
    return {
        "success": True,
        "exception_id": exc.id,
        "status": exc.status
    }
