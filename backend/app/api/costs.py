from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository

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

    return {
        "success": True,
        "saved_skus": len(saved),
        "saved": saved
    }
