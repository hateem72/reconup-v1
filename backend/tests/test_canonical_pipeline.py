import pytest
import pandas as pd
from app.schemas.canonical import CanonicalOrder, CanonicalPayment
from app.finance.profiler import profile_sheet, profile_column
from app.finance.header_detector import detect_header_and_data_rows
from app.finance.order_normalizer import auto_map_order_columns, validate_order_mapping, normalize_canonical_orders
from app.finance.payment_normalizer import auto_map_payment_columns, validate_payment_mapping, normalize_canonical_payments

def test_canonical_order_model():
    order = CanonicalOrder(
        order_id="ORD1001",
        sku="LOVEAGR",
        quantity=2,
        status="Delivered",
        source_file="test_orders.xlsx",
        source_sheet="Order Details",
        source_row=5
    )
    assert order.order_id == "ORD1001"
    assert order.sku == "LOVEAGR"
    assert order.quantity == 2
    assert order.status == "Delivered"
    assert order.source_row == 5

def test_canonical_payment_multi_event():
    payment1 = CanonicalPayment(
        transaction_id="trx_1",
        order_id="ORD1001",
        settlement_amount=1000.0,
        transaction_type="SETTLEMENT",
        adjustment_reason="Order Settlement"
    )
    payment2 = CanonicalPayment(
        transaction_id="trx_2",
        order_id="ORD1001",
        settlement_amount=-50.0,
        transaction_type="DEDUCTION",
        adjustment_reason="Platform Fee"
    )
    assert payment1.order_id == payment2.order_id
    assert payment1.settlement_amount == 1000.0
    assert payment2.settlement_amount == -50.0

def test_column_profiler():
    df = pd.DataFrame({
        "Sub Order No": ["ORD101", "ORD102", "ORD103", "ORD104"],
        "Quantity": [1, 2, 1, 3],
        "Status": ["Delivered", "Delivered", "Return", "Cancelled"]
    })
    sheet_prof = profile_sheet(df, "Order Sheet", 0)
    assert sheet_prof.row_count == 4
    assert sheet_prof.column_count == 3
    assert len(sheet_prof.column_profiles) == 3

def test_header_detection():
    df = pd.DataFrame([
        ["My Company Report", "", ""],
        ["Report Title: Orders", "", ""],
        ["Sub Order No", "Seller SKU", "Quantity"],
        ["ORD101", "SKU-A", 1]
    ])
    header_idx, data_idx = detect_header_and_data_rows(df)
    assert header_idx == 2
    assert data_idx == 3

def test_order_auto_mapping_and_validation():
    headers = ["Sub Order Number", "Seller SKU", "Units", "Live Order Status"]
    mapping = auto_map_order_columns(headers)
    assert mapping["order_id"] == "Sub Order Number"
    assert mapping["sku"] == "Seller SKU"
    assert mapping["quantity"] == "Units"
    assert mapping["status"] == "Live Order Status"

    df_data = pd.DataFrame({
        "Sub Order Number": ["ORD1", "ORD2", "ORD3"],
        "Seller SKU": ["SKU1", "SKU2", "SKU1"],
        "Units": [1, 2, 1],
        "Live Order Status": ["Delivered", "Delivered", "Return"]
    })
    is_valid, errors = validate_order_mapping(df_data, mapping)
    assert is_valid is True
    assert len(errors) == 0

    canonical_orders = normalize_canonical_orders(df_data, mapping, "test.xlsx", "Sheet1", 2)
    assert len(canonical_orders) == 3
    assert canonical_orders[0].order_id == "ORD1"
    assert canonical_orders[0].status == "Delivered"

def test_payment_multi_event_normalization():
    headers = ["Sub Order No", "Final Settlement Amount", "Reason for Credit Entry"]
    mapping = auto_map_payment_columns(headers)
    assert mapping["order_id"] == "Sub Order No"
    assert mapping["settlement_amount"] == "Final Settlement Amount"

    df_payment = pd.DataFrame({
        "Sub Order No": ["ORD1", "ORD1", "ORD1"],
        "Final Settlement Amount": [1000.0, -50.0, -20.0],
        "Reason for Credit Entry": ["Settlement", "Platform Fee", "Return Penalty"]
    })
    canonical_payments = normalize_canonical_payments(df_payment, mapping, "payment.xlsx", "Payments", 2)
    assert len(canonical_payments) == 3
    assert canonical_payments[0].order_id == "ORD1"
    assert canonical_payments[0].settlement_amount == 1000.0
    assert canonical_payments[1].settlement_amount == -50.0
    assert canonical_payments[2].settlement_amount == -20.0
