from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.finance.reconciliation import reconcile_canonical_records

router = APIRouter()

@router.get("/batches/{batch_id}/reconciliation")
def get_batch_reconciliation(batch_id: str, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    batch = repo.get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    orders = repo.get_canonical_orders(batch_id)
    payments = repo.get_canonical_payments(batch_id)

    rec_res = reconcile_canonical_records(orders, payments)
    
    matched = rec_res.get("matched", [])
    missing_in_pmt = rec_res.get("missingInPayment", [])
    missing_in_ord = rec_res.get("missingInOrder", [])
    
    all_records = []
    for m in matched:
        all_records.append({
            "order_id": m.get("orderId"),
            "order_date": m.get("orderDate"),
            "product_details": m.get("productDetails"),
            "qty": m.get("qty"),
            "order_status": m.get("orderSheetStatus"),
            "payment_status": m.get("paymentStatuses"),
            "payment_amount": m.get("totalPayment"),
            "match_status": "MATCHED",
            "confidence": 1.0,
            "reason": "Matched Order Sheet ID with Payment Settlement events"
        })

    for m in missing_in_pmt:
        all_records.append({
            "order_id": m.get("orderId"),
            "order_date": m.get("orderDate"),
            "product_details": m.get("productDetails"),
            "qty": m.get("qty"),
            "order_status": m.get("orderSheetStatus"),
            "payment_status": "MISSING",
            "payment_amount": 0.0,
            "match_status": "MISSING_PAYMENT",
            "confidence": 0.0,
            "reason": "Order recorded in Master Manifest but no settlement entry found"
        })

    for m in missing_in_ord:
        all_records.append({
            "order_id": m.get("orderId"),
            "order_date": m.get("orderDate"),
            "product_details": m.get("productDetails"),
            "qty": m.get("qty"),
            "order_status": "N/A (Historical)",
            "payment_status": m.get("paymentStatuses"),
            "payment_amount": m.get("totalPayment"),
            "match_status": "HISTORICAL_PAYMENT",
            "confidence": 0.5,
            "reason": "Payment line referencing order from previous settlement month"
        })

    return {
        "batch_id": batch_id,
        "total_records": rec_res.get("totalOrders", len(orders)),
        "matched_count": len(matched),
        "missing_payment_count": len(missing_in_pmt),
        "historical_payment_count": len(missing_in_ord),
        "match_rate": rec_res.get("matchRate", 0.0),
        "count_delivered": rec_res.get("countDelivered", 0),
        "count_returns": rec_res.get("countReturns", 0),
        "count_rto": rec_res.get("countRTO", 0),
        "records": all_records,
        "raw_reconciliation": rec_res
    }
