import pytest
from app.finance.profit_calculator import (
    group_by_sku,
    calculate_sku_profit,
    calculate_overall_profit,
    get_unique_skus,
    resolve_cost_per_unit
)

def test_group_by_sku():
    data = [
        {"skuId": "A", "status": "Delivered", "amount": "100", "quantity": "1"},
        {"skuId": "B", "status": "Delivered", "amount": "200", "quantity": "1"},
        {"skuId": "A", "status": "Return", "amount": "-50", "quantity": "1"},
    ]
    grouped = group_by_sku(data)
    assert set(grouped.keys()) == {"A", "B"}
    assert len(grouped["A"]) == 2
    assert len(grouped["B"]) == 1
    assert grouped["A"][0]["status"] == "Delivered"
    assert grouped["A"][0]["amount"] == 100.0


def test_calculate_sku_profit_delivered():
    items = [
        {"status": "Delivered", "amount": 500, "quantity": 1}
    ]
    result = calculate_sku_profit(items, cost_per_unit=100)
    assert result["deliveredSales"] == 500.0
    assert result["deliveredCount"] == 1
    assert result["totalCost"] == 100.0
    assert result["finalProfit"] == 400.0
    assert result["isProfitable"] is True


def test_calculate_sku_profit_returns_and_claims():
    items = [
        {"status": "Delivered", "amount": 500, "quantity": 1},
        {"status": "Return", "amount": -50, "quantity": 1},
        {"status": "Claim", "amount": 200, "quantity": 1},
        {"status": "Affiliate Fees", "amount": 100, "quantity": 1},
        {"status": "Exchange", "amount": 75, "quantity": 1}
    ]
    result = calculate_sku_profit(items, cost_per_unit=0)
    assert result["returnPenalty"] == 50.0
    assert result["claim"] == 200.0
    assert result["affiliateFees"] == 100.0
    assert result["exchange"] == 75.0
    # Formula: (500 + 0) - 50 - 0 + 200 - 100 + 75 = 625
    assert result["finalProfit"] == 625.0


def test_calculate_sku_profit_cancelled_treated_as_delivered():
    items = [
        {"status": "Cancelled", "amount": 300, "quantity": 2}
    ]
    result = calculate_sku_profit(items, cost_per_unit=50)
    assert result["cancelledCount"] == 2
    assert result["cancelledSales"] == 300.0
    # Cost = 2 * 50 = 100
    assert result["totalCost"] == 100.0
    # Profit = 300 - 100 = 200
    assert result["finalProfit"] == 200.0


def test_resolve_cost_per_unit_composite():
    costs = {
        "LOVEAGR": 15,
        "cp_SNGLN335": 35,
        "pkg_SNGLN335": 3
    }
    assert resolve_cost_per_unit("LOVEAGR", costs) == 15.0
    assert resolve_cost_per_unit("SNGLN335", costs) == 38.0
    assert resolve_cost_per_unit("UNKNOWN", costs) == 0.0


def test_calculate_overall_profit():
    grouped = {
        "SKU1": [{"status": "Delivered", "amount": 500, "quantity": 1}],
        "SKU2": [{"status": "Delivered", "amount": 300, "quantity": 1}]
    }
    costs = {"SKU1": 100, "SKU2": 50}
    result = calculate_overall_profit(grouped, costs)
    overall = result["overall"]
    assert overall["totalProfit"] == 650.0 # (500-100) + (300-50)
    assert overall["totalDeliveredCount"] == 2
    assert set(result["skuBreakdowns"].keys()) == {"SKU1", "SKU2"}


def test_get_unique_skus():
    data = [{"skuId": "C"}, {"skuId": "A"}, {"skuId": "B"}, {"skuId": "A"}]
    assert get_unique_skus(data) == ["A", "B", "C"]
