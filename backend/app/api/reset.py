from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import (
    BatchModel,
    FileModel,
    SheetModel,
    OrderModel,
    PaymentModel,
    ReconciliationResultModel,
    ExceptionModel,
    AgentDecisionModel,
    ReportModel,
    AuditEventModel
)
from app.core.logging import log_stage

router = APIRouter()

@router.post("/reset")
def hard_reset_system(keep_rules_and_costs: bool = True, db: Session = Depends(get_db)):
    """
    Hard resets the system by clearing all stored batches, orders, payments,
    reconciliation results, surfaced exceptions, decisions, reports, and audit logs.
    """
    log_stage("SYSTEM", f"Initiating Hard Reset (keep_rules_and_costs={keep_rules_and_costs})")
    
    try:
        db.query(ReconciliationResultModel).delete()
        db.query(ExceptionModel).delete()
        db.query(AgentDecisionModel).delete()
        db.query(ReportModel).delete()
        db.query(AuditEventModel).delete()
        db.query(OrderModel).delete()
        db.query(PaymentModel).delete()
        db.query(SheetModel).delete()
        db.query(FileModel).delete()
        db.query(BatchModel).delete()
        
        db.commit()
        log_stage("SYSTEM", "Hard reset completed successfully. Database cleared and pipeline ready for fresh start.")
        
        return {
            "success": True,
            "message": "System hard reset complete. All batches, orders, payments, reconciliation results, and exceptions cleared.",
            "pipeline_step": 1
        }
    except Exception as e:
        db.rollback()
        log_stage("SYSTEM", f"Hard reset failed: {str(e)}", level="error")
        return {
            "success": False,
            "error": str(e)
        }
