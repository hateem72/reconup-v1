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
from app.core.redis_client import redis_client

router = APIRouter()

@router.post("/reset")
def hard_reset_system(keep_rules_and_costs: bool = True, db: Session = Depends(get_db)):
    """
    Hard resets the system by clearing all stored batches, orders, payments,
    reconciliation results, surfaced exceptions, decisions, reports, audit logs, and Redis schema caches.
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

        # Flush Redis schema fingerprint cache
        flushed_cache_keys = redis_client.flush_pattern("schema:*")

        log_stage("SYSTEM", f"Hard reset completed successfully. Database and {flushed_cache_keys} cache keys cleared.")
        
        return {
            "success": True,
            "message": "System hard reset complete. All batches, orders, payments, reconciliation results, and Redis caches cleared.",
            "flushed_cache_keys": flushed_cache_keys,
            "pipeline_step": 1
        }
    except Exception as e:
        db.rollback()
        log_stage("SYSTEM", f"Hard reset failed: {str(e)}", level="error")
        return {
            "success": False,
            "error": str(e)
        }
