import pytest
from app.finance.reconciliation import process_reconciliation
from app.finance.exception_detector import detect_unknown_patterns

def test_process_reconciliation_matching():
    orders = [
        {"Sub Order No": "ORD1001", "Order Date": "2026-08-01", "Product Name": "Widget", "SKU": "SKU1", "Quantity": 1, "Reason for Credit Entry": "Delivered"},
        {"Sub Order No": "ORD1002", "Order Date": "2026-08-01", "Product Name": "Gadget", "SKU": "SKU2", "Quantity": 1, "Reason for Credit Entry": "Delivered"}
    ]
    payments = [
        [], [], [], # 3 header rows
        ["ORD1001", "2026-08-01", "2026-08-01", "", "SKU1", "", "", "Delivered", "", "", 1, "", "", 500.0],
        ["ORD1002", "2026-08-01", "2026-08-01", "", "SKU2", "", "", "Return", "", "", 1, "", "", -50.0]
    ]

    result = process_reconciliation(orders, payments)
    assert result["totalOrders"] == 2
    assert result["matchedCount"] == 2
    assert result["matchRate"] == 100.0
    assert len(result["missingInPayment"]) == 0


def test_process_reconciliation_missing_payment():
    orders = [
        {"Sub Order No": "ORD1001", "Order Date": "2026-08-01", "SKU": "SKU1", "Quantity": 1, "Reason for Credit Entry": "Delivered"},
        {"Sub Order No": "ORD1003", "Order Date": "2026-08-01", "SKU": "SKU3", "Quantity": 1, "Reason for Credit Entry": "Delivered"}
    ]
    payments = [
        [], [], [],
        ["ORD1001", "2026-08-01", "", "", "SKU1", "", "", "Delivered", "", "", 1, "", "", 500.0]
    ]

    result = process_reconciliation(orders, payments)
    assert result["totalOrders"] == 2
    assert result["matchedCount"] == 1
    assert result["matchRate"] == 50.0
    assert len(result["missingInPayment"]) == 1
    assert result["missingInPayment"][0]["orderId"] == "ORD1003"


def test_detect_unknown_patterns():
    records = [
        {"orderId": "ORD1", "status": "Delivered", "amount": 100},
        {"orderId": "ORD2", "status": "Return Assurance Fee", "amount": -20},
        {"orderId": "ORD3", "status": "Return Assurance Fee", "amount": -20},
    ]
    unknowns = detect_unknown_patterns(records)
    assert len(unknowns) == 1
    assert unknowns[0]["raw_status"] == "Return Assurance Fee"
    assert unknowns[0]["occurrences"] == 2
    assert unknowns[0]["amount"] == -40.0
