from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.agents.core.llm_factory import get_llm

router = APIRouter()

class QARequest(BaseModel):
    question: str
    batch_id: Optional[str] = None

@router.post("/qa")
def ask_finance_question(req: QARequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    q = req.question.strip()
    
    # 1. Fetch structured database facts
    context_facts = {}
    if req.batch_id:
        batch = repo.get_batch(req.batch_id)
        report = repo.get_latest_report(req.batch_id)
        reconciliations = repo.get_reconciliation_results(req.batch_id)
        exceptions = repo.get_exceptions(req.batch_id)

        context_facts = {
            "batch_id": req.batch_id,
            "status": batch.status if batch else "UNKNOWN",
            "total_records": batch.total_records if batch else 0,
            "summary": report.summary_json if report else {},
            "match_rate": report.match_rate if report else 0.0,
            "total_profit": report.total_profit if report else 0.0,
            "unresolved_exceptions_count": len([e for e in exceptions if e.status == "PENDING"]),
            "unresolved_exceptions": [
                {"order_id": e.order_id, "type": e.exception_type, "status": e.raw_status, "amount": e.amount}
                for e in exceptions if e.status == "PENDING"
            ][:10]
        }

    # 2. Invoke LLM with facts
    llm = get_llm(temperature=0.0)
    prompt = f"""
System: You are an AI Finance Controller. Answer the user question using ONLY the provided structured database facts. Never guess or hallucinate financial numbers.

Structured Facts:
{context_facts}

User Question: {q}

Answer:
"""
    try:
        response = llm.invoke(prompt)
        answer_text = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        answer_text = f"Finance Analysis: Based on batch database records, total profit is ₹{context_facts.get('total_profit', 0.0)} with match rate {context_facts.get('match_rate', 0.0)}%."

    return {
        "question": q,
        "answer": answer_text,
        "retrieved_facts": context_facts
    }
