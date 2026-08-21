from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository

router = APIRouter()

@router.get("/batches/{batch_id}/reconciliation")
def get_batch_reconciliation(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    results = repo.get_reconciliation_results(batch_id)
    batch = repo.get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    matched_count = len([r for r in results if r.match_status == "MATCHED"])
    missing_payment_count = len([r for r in results if r.match_status == "MISSING_PAYMENT"])
    missing_order_count = len([r for r in results if r.match_status == "MISSING_ORDER"])
    
    total = max(batch.total_records, 1)
    match_rate = round((matched_count / total) * 100.0, 2)

    return {
        "batch_id": batch_id,
        "total_records": batch.total_records,
        "matched_count": matched_count,
        "missing_payment_count": missing_payment_count,
        "missing_order_count": missing_order_count,
        "match_rate": match_rate,
        "records": [
            {
                "id": r.id,
                "order_id": r.order_id,
                "match_status": r.match_status,
                "order_status": r.order_status,
                "payment_status": r.payment_status,
                "payment_amount": r.payment_amount,
                "confidence": r.confidence,
                "reason": r.reason
            }
            for r in results
        ]
    }
