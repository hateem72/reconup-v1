from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository

router = APIRouter()

@router.get("/batches/{batch_id}/report")
def get_batch_report(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    report = repo.get_latest_report(batch_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this batch")

    return {
        "batch_id": batch_id,
        "match_rate": report.match_rate,
        "resolved_count": report.resolved_count,
        "unresolved_count": report.unresolved_count,
        "total_profit": report.total_profit,
        "total_revenue": report.total_revenue,
        "total_deductions": report.total_deductions,
        "created_at": report.created_at,
        "summary": report.summary_json,
        "sku_breakdown": report.sku_breakdown_json
    }
