from typing import List, Dict, Any, Union
from app.finance.normalizer import normalize_status, validate_and_clean_amount, clean_quantity

def group_by_sku(data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groups sales data by SKU ID and normalizes amounts, statuses, and quantities.
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}

    for row in data:
        sku_id = str(row.get("skuId") or "").strip()
        if not sku_id:
            continue

        if sku_id not in grouped:
            grouped[sku_id] = []

        raw_status = str(row.get("status") or "")
        norm_status = normalize_status(raw_status)
        
        _, amount, _ = validate_and_clean_amount(row.get("amount", 0))
        quantity = clean_quantity(row.get("quantity"), default=1)
        
        _, claim, _ = validate_and_clean_amount(row.get("claim", row.get("compensation", 0)))
        _, affiliate, _ = validate_and_clean_amount(row.get("affiliateFees", row.get("advertisement", 0)))

        grouped[sku_id].append({
            **row,
            "skuId": sku_id,
            "status": norm_status,
            "rawStatus": raw_status,
            "amount": amount,
            "quantity": quantity,
            "claim": claim,
            "affiliateFees": affiliate,
            "compensation": claim,
            "advertisement": affiliate
        })

    return grouped


def calculate_sku_profit(items: List[Dict[str, Any]], cost_per_unit: float = 0.0) -> Dict[str, Any]:
    """
    Calculates profit for a single SKU based on reference business logic.
    """
    delivered_sales = 0.0
    delivered_count = 0
    cancelled_sales = 0.0
    cancelled_count = 0
    shipped_count = 0
    return_penalty = 0.0
    return_count = 0
    rto_count = 0
    total_claim = 0.0
    total_affiliate_fees = 0.0
    total_exchange = 0.0

    quantity_breakdown = {
        "delivered": {},
        "return": {},
        "rto": {},
        "shipping": {},
        "cancelled": {}
    }

    for item in items:
        status = str(item.get("status", "")).lower()
        amount = float(item.get("amount", 0.0))
        qty = int(item.get("quantity", 1))

        if "deliver" in status:
            delivered_sales += amount
            delivered_count += qty
            qty_str = str(qty)
            quantity_breakdown["delivered"][qty_str] = quantity_breakdown["delivered"].get(qty_str, 0) + 1
        elif "cancel" in status:
            # Cancelled treated as Delivered for profit calculation (revenue + cost incurred)
            cancelled_sales += amount
            cancelled_count += qty
            qty_str = str(qty)
            quantity_breakdown["cancelled"][qty_str] = quantity_breakdown["cancelled"].get(qty_str, 0) + 1
        elif "shipped" in status or "shipping" in status:
            shipped_count += qty
            qty_str = str(qty)
            quantity_breakdown["shipping"][qty_str] = quantity_breakdown["shipping"].get(qty_str, 0) + 1
        elif "return" in status:
            return_penalty += abs(amount)
            return_count += qty
            qty_str = str(qty)
            quantity_breakdown["return"][qty_str] = quantity_breakdown["return"].get(qty_str, 0) + 1
        elif "rto" in status:
            rto_count += qty
            qty_str = str(qty)
            quantity_breakdown["rto"][qty_str] = quantity_breakdown["rto"].get(qty_str, 0) + 1
        elif "compensation" in status or "claim" in status:
            total_claim += abs(amount)
        elif "advertisement" in status or "advertise" in status or "affiliate" in status:
            total_affiliate_fees += abs(amount)
        elif "exchange" in status:
            total_exchange += amount

    # Cancelled items treated as delivered for unit cost calculation
    total_cost = (delivered_count + cancelled_count) * cost_per_unit
    
    # Deterministic Formula: (Sales + CancelledSales) - ReturnPenalties - Cost + Claims - AffiliateFees + Exchange
    final_profit = (delivered_sales + cancelled_sales) - return_penalty - total_cost + total_claim - total_affiliate_fees + total_exchange

    return {
        "deliveredSales": round(delivered_sales, 4),
        "deliveredCount": delivered_count,
        "cancelledSales": round(cancelled_sales, 4),
        "cancelledCount": cancelled_count,
        "shippedCount": shipped_count,
        "returnPenalty": round(return_penalty, 4),
        "returnCount": return_count,
        "rtoCount": rto_count,
        "totalCost": round(total_cost, 4),
        "costPerUnit": round(cost_per_unit, 4),
        "claim": round(total_claim, 4),
        "affiliateFees": round(total_affiliate_fees, 4),
        "compensation": round(total_claim, 4),
        "advertisement": round(total_affiliate_fees, 4),
        "exchange": round(total_exchange, 4),
        "finalProfit": round(final_profit, 4),
        "isProfitable": final_profit > 0,
        "quantityBreakdown": quantity_breakdown
    }


def resolve_cost_per_unit(sku_id: str, costs: Dict[str, Any]) -> float:
    """
    Resolves total cost per unit for a given SKU ID from cost dict.
    Supports direct SKU key (e.g. costs['LOVEAGR'] = 15) or composite keys
    (e.g. cp_LOVEAGR = 12, pkg_LOVEAGR = 3 => 15).
    """
    if not costs:
        return 0.0

    if sku_id in costs and isinstance(costs[sku_id], (int, float)):
        return float(costs[sku_id])

    cp_key = f"cp_{sku_id}"
    pkg_key = f"pkg_{sku_id}"
    
    cost_price = float(costs.get(cp_key, 0.0))
    packaging_cost = float(costs.get(pkg_key, 0.0))
    
    if cost_price > 0 or packaging_cost > 0:
        return cost_price + packaging_cost

    return 0.0


def calculate_overall_profit(grouped_data: Dict[str, List[Dict[str, Any]]], costs: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calculates aggregated profit analysis across all SKUs.
    """
    if costs is None:
        costs = {}

    sku_breakdowns: Dict[str, Dict[str, Any]] = {}
    total_profit = 0.0
    total_delivered_sales = 0.0
    total_cancelled_sales = 0.0
    total_return_penalty = 0.0
    total_cost = 0.0
    total_claim = 0.0
    total_affiliate_fees = 0.0
    total_exchange = 0.0
    total_delivered_count = 0
    total_cancelled_count = 0
    total_shipped_count = 0
    total_return_count = 0
    total_rto_count = 0

    for sku_id, items in grouped_data.items():
        unit_cost = resolve_cost_per_unit(sku_id, costs)
        breakdown = calculate_sku_profit(items, unit_cost)
        sku_breakdowns[sku_id] = breakdown

        total_profit += breakdown["finalProfit"]
        total_delivered_sales += breakdown["deliveredSales"]
        total_cancelled_sales += breakdown["cancelledSales"]
        total_return_penalty += breakdown["returnPenalty"]
        total_cost += breakdown["totalCost"]
        total_claim += breakdown["claim"]
        total_affiliate_fees += breakdown["affiliateFees"]
        total_exchange += breakdown["exchange"]
        total_delivered_count += breakdown["deliveredCount"]
        total_cancelled_count += breakdown["cancelledCount"]
        total_shipped_count += breakdown["shippedCount"]
        total_return_count += breakdown["returnCount"]
        total_rto_count += breakdown["rtoCount"]

    total_items = (
        total_delivered_count +
        total_cancelled_count +
        total_shipped_count +
        total_return_count +
        total_rto_count
    )

    return {
        "skuBreakdowns": sku_breakdowns,
        "overall": {
            "totalProfit": round(total_profit, 4),
            "totalDeliveredSales": round(total_delivered_sales, 4),
            "totalCancelledSales": round(total_cancelled_sales, 4),
            "totalReturnPenalty": round(total_return_penalty, 4),
            "totalCost": round(total_cost, 4),
            "totalClaim": round(total_claim, 4),
            "totalAffiliateFees": round(total_affiliate_fees, 4),
            "totalCompensation": round(total_claim, 4),
            "totalAdvertisement": round(total_affiliate_fees, 4),
            "totalExchange": round(total_exchange, 4),
            "totalDeliveredCount": total_delivered_count,
            "totalCancelledCount": total_cancelled_count,
            "totalShippedCount": total_shipped_count,
            "totalReturnCount": total_return_count,
            "totalRTOCount": total_rto_count,
            "totalItems": total_items,
            "isProfitable": total_profit > 0
        }
    }


def get_unique_skus(data: List[Dict[str, Any]]) -> List[str]:
    """Extracts sorted unique SKU IDs from sales data."""
    skus = set()
    for row in data:
        sku = str(row.get("skuId") or "").strip()
        if sku:
            skus.add(sku)
    return sorted(list(skus))
