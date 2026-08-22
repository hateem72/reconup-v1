from typing import List, Dict, Any, Tuple
from app.schemas.canonical import CanonicalOrder, CanonicalPayment
from app.core.logging import log_stage

def process_reconciliation(orders_raw: List[Dict[str, Any]], payments_raw: List[Any]) -> Dict[str, Any]:
    """
    Reconciles Order Sheet records against multi-line Payment settlement records.
    The Order Sheet is the MASTER ANCHOR set. Extra payment entries for historical orders
    not present in the current Order Sheet are categorized separately and DO NOT penalize match rate.
    """
    log_stage("RECONCILER", f"Starting reconciliation: Master Order Sheet ({len(orders_raw)} orders) vs Payment Settlement ({len(payments_raw)} lines)")
    
    # 1. Process Master Order Sheet
    orders = []
    for row in orders_raw:
        order_id = str(row.get("Sub Order No", row.get("orderId", "")) or "").strip()
        if not order_id:
            continue
            
        status = str(row.get("Reason for Credit Entry", row.get("orderStatus", "")) or "").strip()
        if status.upper() == "CANCELLED":
            continue
            
        orders.append({
            "orderId": order_id,
            "orderDate": str(row.get("Order Date", row.get("orderDate", "")) or ""),
            "productName": str(row.get("Product Name", row.get("productName", "")) or ""),
            "sku": str(row.get("SKU", row.get("sku", "")) or ""),
            "qty": int(row.get("Quantity", row.get("qty", 1)) or 1),
            "orderStatus": status
        })

    # 2. Process Multi-Event Payment Settlement Sheet
    payment_rows = payments_raw[3:] if len(payments_raw) > 3 and isinstance(payments_raw[0], list) else payments_raw
    payment_map: Dict[str, Dict[str, Any]] = {}
    compensation_fees: List[Dict[str, Any]] = []
    total_payments = 0

    for row in payment_rows:
        if isinstance(row, dict):
            order_id = str(row.get("orderId", row.get("Order ID", "")) or "").strip()
            amount = float(row.get("amount", row.get("Payment Amount", 0)) or 0)
            payment_status = str(row.get("status", row.get("Payment Status", "")) or "").strip()
            qty = int(row.get("qty", row.get("Quantity", 1)) or 1)
            order_date = str(row.get("orderDate", ""))
            product_code = str(row.get("sku", ""))
        elif isinstance(row, (list, tuple)):
            if not row or len(row) == 0:
                continue
            order_id = str(row[0] or "").strip()
            if not order_id:
                continue
            total_payments += 1
            
            amount = float(row[13]) if len(row) > 13 and row[13] is not None else 0.0
            payment_status = str(row[7] if len(row) > 7 and row[7] is not None else "").strip()
            qty = int(row[10]) if len(row) > 10 and row[10] is not None else 1
            order_date = str(row[1] if len(row) > 1 else (row[2] if len(row) > 2 else ""))
            product_code = str(row[4] if len(row) > 4 else "")
        else:
            continue

        if not order_id:
            continue

        if payment_status.upper() == "CANCELLED":
            continue

        # Rule: Blank status goes to Compensation
        if not payment_status:
            compensation_fees.append({
                "orderId": order_id,
                "orderDate": order_date,
                "paymentAmount": amount,
                "qty": qty,
                "rawRow": row
            })
            continue

        # Aggregate multi-line settlement entries for the same order_id
        if order_id not in payment_map:
            payment_map[order_id] = {
                "orderId": order_id,
                "orderDate": order_date,
                "productCode": product_code,
                "statuses": set([payment_status]),
                "totalPayment": amount,
                "qty": qty,
                "processed": False
            }
        else:
            payment_map[order_id]["statuses"].add(payment_status)
            payment_map[order_id]["totalPayment"] += amount
            payment_map[order_id]["qty"] += qty

    # 3. Match Master Order Sheet against Multi-Event Payment Map
    matched: List[Dict[str, Any]] = []
    missing_in_payment: List[Dict[str, Any]] = []
    
    count_delivered = 0
    count_returns = 0
    count_rto = 0

    order_map = {}
    for order in orders:
        oid = order["orderId"]
        order_map[oid] = order

        if oid in payment_map:
            pm = payment_map[oid]
            joined_status = " + ".join(sorted(list(pm["statuses"])))
            
            matched.append({
                "orderId": oid,
                "orderDate": order["orderDate"],
                "productDetails": order["sku"] or order["productName"],
                "qty": order["qty"],
                "orderSheetStatus": order["orderStatus"],
                "paymentStatuses": joined_status,
                "totalPayment": round(pm["totalPayment"], 4),
                "matchStatus": "MATCHED"
            })

            joined_upper = joined_status.upper()
            if "DELIVERED" in joined_upper:
                count_delivered += 1
            if "RETURN" in joined_upper:
                count_returns += 1
            if "RTO" in joined_upper:
                count_rto += 1

            pm["processed"] = True
        else:
            missing_in_payment.append({
                "orderId": oid,
                "orderDate": order["orderDate"],
                "productDetails": order["sku"] or order["productName"],
                "qty": order["qty"],
                "orderSheetStatus": order["orderStatus"],
                "matchStatus": "MISSING_PAYMENT"
            })

    # Unmatched payment lines referencing historical order IDs not in current Order Sheet
    missing_in_order = []
    for oid, pm in payment_map.items():
        if not pm["processed"]:
            joined_status = " + ".join(sorted(list(pm["statuses"])))
            missing_in_order.append({
                "orderId": oid,
                "orderDate": pm["orderDate"],
                "productDetails": pm["productCode"],
                "qty": pm["qty"],
                "paymentStatuses": joined_status,
                "totalPayment": round(pm["totalPayment"], 4),
                "matchStatus": "HISTORICAL_PAYMENT_ROW"
            })

    # Match Rate is calculated STRICTLY against Master Order Sheet count
    total_orders = len(orders)
    matched_count = len(matched)
    match_rate = (matched_count / total_orders * 100.0) if total_orders > 0 else 0.0

    log_stage("RECONCILER", f"Order Sheet Match Result: {matched_count}/{total_orders} matched ({round(match_rate, 2)}% match rate). Found {len(missing_in_order)} historical payment rows.")

    return {
        "matched": matched,
        "missingInPayment": missing_in_payment,
        "missingInOrder": missing_in_order,
        "compensationFees": compensation_fees,
        "totalOrders": total_orders,
        "totalPayments": total_payments or len(payment_map),
        "matchedCount": matched_count,
        "matchRate": round(match_rate, 2),
        "countDelivered": count_delivered,
        "countReturns": count_returns,
        "countRTO": count_rto
    }


def reconcile_canonical_records(canonical_orders: List[CanonicalOrder], canonical_payments: List[CanonicalPayment]) -> Dict[str, Any]:
    """Bridges CanonicalOrder and CanonicalPayment lists directly into reconciliation engine."""
    orders_raw = [
        {
            "Sub Order No": o.order_id,
            "SKU": o.sku,
            "Product Name": o.product_name,
            "Quantity": o.quantity,
            "Reason for Credit Entry": o.status,
            "Order Date": o.order_date
        }
        for o in canonical_orders
    ]
    payments_raw = [
        {
            "orderId": p.order_id,
            "amount": p.settlement_amount,
            "status": p.status,
            "qty": p.quantity,
            "orderDate": p.payment_date,
            "sku": p.sku
        }
        for p in canonical_payments
    ]
    return process_reconciliation(orders_raw, payments_raw)
