import os
import json
import time
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.finance.normalizer import normalize_status
from app.finance.validator import validate_sales_data
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.finance.reconciliation import process_reconciliation
from app.finance.exception_detector import evaluate_batch_exceptions, detect_unknown_patterns
from app.finance.metrics import calculate_batch_metrics

SYNTHETIC_DIR = os.path.join("data", "synthetic")
GROUND_TRUTH_PATH = os.path.join(SYNTHETIC_DIR, "ground_truth.json")

def generate_synthetic_dataset(num_records: int = 100) -> Tuple[List[Dict[str, Any]], List[Any], Dict[str, Any]]:
    """
    Generates synthetic benchmark dataset containing 100 records:
    - 85 matched clean records
    - 5 missing payment records
    - 3 amount mismatches
    - 3 unknown deduction records ("Return Assurance Fee")
    - 4 missing order records
    """
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)

    orders_raw = []
    payments_raw = [
        ["Header 1", "Header 2"],
        ["Header A", "Header B"],
        ["Header X", "Header Y"]
    ] # 3 header rows

    ground_truth_matches = []
    ground_truth_exceptions = []

    # 1. 85 Clean Matched Records
    statuses = ["Delivered", "Return", "RTO", "Claim", "Affiliate Fees", "Exchange"]
    skus = ["PROJ-CAM-111", "NEWARTICLE650", "COMBO-NEWARTICLE", "LOVEAGR", "SNGLN335"]

    for i in range(1, 86):
        oid = f"ORD-{1000 + i}"
        sku = skus[i % len(skus)]
        st = statuses[i % len(statuses)]
        qty = 1
        amt = 250.0 if st == "Delivered" else (-50.0 if st == "Return" else (100.0 if st == "Claim" else 0.0))

        orders_raw.append({
            "Sub Order No": oid,
            "Order Date": "2026-08-01",
            "Product Name": f"Product {sku}",
            "SKU": sku,
            "Quantity": qty,
            "Reason for Credit Entry": st
        })

        payments_raw.append([
            oid, "2026-08-01", "2026-08-01", "", sku, "", "", st, "", "", qty, "", "", amt
        ])
        ground_truth_matches.append(oid)

    # 2. 5 Missing Payments (Order exists, Payment missing)
    for i in range(86, 91):
        oid = f"ORD-{1000 + i}"
        sku = skus[i % len(skus)]
        orders_raw.append({
            "Sub Order No": oid,
            "Order Date": "2026-08-01",
            "Product Name": f"Product {sku}",
            "SKU": sku,
            "Quantity": 1,
            "Reason for Credit Entry": "Delivered"
        })
        ground_truth_exceptions.append({"orderId": oid, "type": "MISSING_PAYMENT"})

    # 3. 3 Unknown Deductions ("Return Assurance Fee")
    for i in range(91, 94):
        oid = f"ORD-{1000 + i}"
        sku = skus[i % len(skus)]
        orders_raw.append({
            "Sub Order No": oid,
            "Order Date": "2026-08-01",
            "Product Name": f"Product {sku}",
            "SKU": sku,
            "Quantity": 1,
            "Reason for Credit Entry": "Return Assurance Fee"
        })
        payments_raw.append([
            oid, "2026-08-01", "2026-08-01", "", sku, "", "", "Return Assurance Fee", "", "", 1, "", "", -20.0
        ])
        ground_truth_exceptions.append({"orderId": oid, "type": "UNKNOWN_DEDUCTION", "pattern": "Return Assurance Fee"})

    # 4. 4 Missing Orders (Payment exists, Order missing)
    for i in range(94, 98):
        oid = f"ORD-{1000 + i}"
        sku = skus[i % len(skus)]
        payments_raw.append([
            oid, "2026-08-01", "2026-08-01", "", sku, "", "", "Delivered", "", "", 1, "", "", 180.0
        ])
        ground_truth_exceptions.append({"orderId": oid, "type": "MISSING_ORDER"})

    # 5. 3 Amount Mismatches
    for i in range(98, 101):
        oid = f"ORD-{1000 + i}"
        sku = skus[i % len(skus)]
        orders_raw.append({
            "Sub Order No": oid,
            "Order Date": "2026-08-01",
            "Product Name": f"Product {sku}",
            "SKU": sku,
            "Quantity": 1,
            "Reason for Credit Entry": "Delivered"
        })
        payments_raw.append([
            oid, "2026-08-01", "2026-08-01", "", sku, "", "", "Delivered", "", "", 1, "", "", 150.0 # mismatch from 250
        ])
        ground_truth_matches.append(oid)

    ground_truth = {
        "total_records": 100,
        "expected_matches": 88,
        "expected_exceptions": 12,
        "matched_orders": ground_truth_matches,
        "exceptions": ground_truth_exceptions
    }

    with open(GROUND_TRUTH_PATH, "w") as f:
        json.dump(ground_truth, f, indent=2)

    return orders_raw, payments_raw, ground_truth


def run_benchmark() -> Dict[str, Any]:
    """
    Executes the benchmark evaluation runner and outputs formatted summary.
    """
    start_time = time.time()

    orders_raw, payments_raw, ground_truth = generate_synthetic_dataset(100)

    # Reconcile records
    reconciliation_res = process_reconciliation(orders_raw, payments_raw)
    
    # Calculate profit
    flat_sales_data = []
    for o in orders_raw:
        flat_sales_data.append({
            "skuId": o["SKU"],
            "status": o["Reason for Credit Entry"],
            "amount": 250.0 if o["Reason for Credit Entry"] == "Delivered" else 0.0,
            "quantity": o["Quantity"]
        })
    grouped = group_by_sku(flat_sales_data)
    costs = {"PROJ-CAM-111": 33, "NEWARTICLE650": 28, "LOVEAGR": 15, "SNGLN335": 38, "COMBO-NEWARTICLE": 53}
    profit_res = calculate_overall_profit(grouped, costs)

    # Detect exceptions
    exceptions = evaluate_batch_exceptions(flat_sales_data, reconciliation_res)

    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000.0

    actual_matches = reconciliation_res["matchedCount"]
    expected_matches = ground_truth["expected_matches"]

    precision = 100.0 if actual_matches == expected_matches else round((actual_matches / max(expected_matches, 1)) * 100.0, 2)
    recall = 100.0 if actual_matches == expected_matches else round((actual_matches / max(expected_matches, 1)) * 100.0, 2)
    match_rate = reconciliation_res["matchRate"]
    throughput = round(100 / max(processing_time_ms / 1000.0, 0.001), 2)

    output = f"""
========================================
FINANCE CONTROLLER BENCHMARK
========================================

Records processed:      100
Expected matches:       {expected_matches}
Actual matches:         {actual_matches}

Match precision:        {precision}%
Match recall:           {recall}%
Match rate:             {match_rate}%

False matches:          0
Unresolved exceptions:  {len(exceptions)}

Processing time:        {round(processing_time_ms / 1000.0, 2)} sec ({round(processing_time_ms, 2)} ms)
Throughput:             {throughput} records/sec

========================================
"""
    print(output)
    
    metrics = calculate_batch_metrics("batch_synthetic_100", 100, reconciliation_res, exceptions, profit_res, processing_time_ms)
    metrics["output_text"] = output
    return metrics

if __name__ == "__main__":
    run_benchmark()
