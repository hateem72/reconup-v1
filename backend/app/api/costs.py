from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.finance.profit_calculator import group_by_sku, calculate_overall_profit
from app.finance.metrics import calculate_batch_metrics

router = APIRouter()

class SkuCostItem(BaseModel):
    sku_id: str
    cost_price: float
    packaging_cost: Optional[float] = 0.0

class SaveCostsRequest(BaseModel):
    costs: List[SkuCostItem]
    batch_id: Optional[str] = None

@router.get("/costs")
def get_sku_costs(db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    items = repo.get_all_sku_costs()
    return {
        "total_skus": len(items),
        "costs": [
            {
                "id": c.id,
                "sku_id": c.sku_id,
                "cost_price": c.cost_price,
                "packaging_cost": c.packaging_cost,
                "total_cost_per_unit": c.cost_price + c.packaging_cost,
                "updated_at": c.updated_at
            }
            for c in items
        ]
    }

@router.post("/costs")
def save_sku_costs(req: SaveCostsRequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    saved = []
    for item in req.costs:
        sc = repo.save_sku_cost(item.sku_id, item.cost_price, item.packaging_cost or 0.0)
        saved.append({
            "sku_id": sc.sku_id,
            "cost_price": sc.cost_price,
            "packaging_cost": sc.packaging_cost,
            "total_unit_cost": sc.cost_price + sc.packaging_cost
        })

    recalculated_report = None
    # Recalculate profit for batch if batch_id provided
    if req.batch_id:
        report = repo.get_latest_report(req.batch_id)
        if report:
            db_costs = repo.get_sku_costs_map()
            # If report summary exists, recalculate overall profit using updated costs
            summary_json = report.summary_json or {}
            # Fetch reconciliation
            reconciliations = repo.get_reconciliation_results(req.batch_id)
            exceptions = repo.get_exceptions(req.batch_id)

            # Recalculate using active SKU breakdowns
            sku_breakdown = dict(report.sku_breakdown_json or {})
            total_profit = 0.0
            total_cost = 0.0

            for sku_id, b in sku_breakdown.items():
                unit_cost = db_costs.get(sku_id, b.get("costPerUnit", 0.0))
                del_count = b.get("deliveredCount", 0)
                can_count = b.get("cancelledCount", 0)
                sku_total_cost = (del_count + can_count) * unit_cost
                
                # Recalculate profit: (Sales + Cancelled) - ReturnPenalty - TotalCost + Claim - Affiliate + Exchange
                final_profit = (b.get("deliveredSales", 0) + b.get("cancelledSales", 0)) - b.get("returnPenalty", 0) - sku_total_cost + b.get("claim", 0) - b.get("affiliateFees", 0) + b.get("exchange", 0)
                
                b["costPerUnit"] = round(unit_cost, 4)
                b["totalCost"] = round(sku_total_cost, 4)
                b["finalProfit"] = round(final_profit, 4)
                b["isProfitable"] = final_profit > 0
                
                total_profit += final_profit
                total_cost += sku_total_cost

            summary_json["totalProfit"] = round(total_profit, 4)
            summary_json["totalCost"] = round(total_cost, 4)
            summary_json["isProfitable"] = total_profit > 0

            # Save updated report
            metrics = {
                "match_rate": report.match_rate,
                "resolved_exceptions": report.resolved_count,
                "unresolved_exceptions": report.unresolved_count,
                "total_profit": round(total_profit, 4),
                "total_revenue": report.total_revenue,
                "total_deductions": report.total_deductions
            }
            recalculated_report = repo.save_report(req.batch_id, "PROFIT_AND_RECONCILIATION", metrics, summary_json, sku_breakdown)

    return {
        "success": True,
        "saved_skus": len(saved),
        "saved": saved,
        "batch_recalculated": req.batch_id is not None
    }
