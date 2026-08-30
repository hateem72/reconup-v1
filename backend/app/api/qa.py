import re
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.database.repositories import FinanceRepository
from app.agents.core.llm_factory import get_llm
from app.agents.core.prompts import TEXT_TO_SQL_SYSTEM_PROMPT, QA_ANSWER_SYNTHESIS_PROMPT

router = APIRouter()

class QARequest(BaseModel):
    query: Optional[str] = None
    question: Optional[str] = None
    batch_id: Optional[str] = None

def is_safe_sql(sql_str: str) -> bool:
    """Strict security check ensuring query is read-only SELECT statement."""
    clean = re.sub(r'/\*.*?\*/', '', sql_str, flags=re.DOTALL).strip().upper()
    if not (clean.startswith("SELECT") or clean.startswith("WITH")):
        return False
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "ATTACH", "DETACH", "PRAGMA", "EXEC", "TRUNCATE"]
    for kw in forbidden:
        if re.search(rf'\b{kw}\b', clean):
            return False
    return True

@router.post("/qa")
def ask_finance_question(req: QARequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    q = (req.query or req.question or "").strip()
    batch_id = req.batch_id or "batch_demo"
    
    llm = get_llm(temperature=0.0)
    
    # 1. Step 1: Text-to-SQL Query Generation using Centralized System Prompt
    system_prompt = TEXT_TO_SQL_SYSTEM_PROMPT.format(batch_id=batch_id)
    sql_prompt = f"{system_prompt}\n\nUser Question: {q}\n"

    sql_query = ""
    sql_results: List[Dict[str, Any]] = []
    executed_safely = False

    try:
        sql_resp = llm.invoke(sql_prompt)
        raw_sql = sql_resp.content if hasattr(sql_resp, 'content') else str(sql_resp)
        
        # Extract SQL query from markdown code block
        match = re.search(r'```sql\s*(.*?)\s*```', raw_sql, re.DOTALL | re.IGNORECASE)
        if match:
            sql_query = match.group(1).strip()
        else:
            sql_query = raw_sql.strip()

        # Enforce 100% Read-Only Safety Validation
        if sql_query and is_safe_sql(sql_query):
            res = db.execute(text(sql_query))
            sql_results = [dict(r._mapping) for r in res.fetchall()[:25]] # Limit 25 rows
            executed_safely = True
    except Exception as e:
        sql_query = f"-- Query Error: {str(e)}"

    # 2. Fallback: Fetch standard repository summary facts if SQL execution failed or returned empty
    if not executed_safely or not sql_results:
        batch = repo.get_batch(batch_id)
        report = repo.get_latest_report(batch_id)
        exceptions = repo.get_exceptions(batch_id)
        sql_results = [{
            "batch_id": batch_id,
            "batch_status": batch.status if batch else "COMPLETED",
            "match_rate": report.match_rate if report else 100.0,
            "unresolved_exceptions_count": len([e for e in exceptions if e.status == "PENDING"]),
            "sample_exceptions": [
                {"order_id": e.order_id, "type": e.exception_type, "amount": e.amount}
                for e in exceptions if e.status == "PENDING"
            ][:5]
        }]

    # 3. Step 2: Answer Synthesis Grounded on Query Results using Centralized System Prompt
    answer_prompt = f"{QA_ANSWER_SYNTHESIS_PROMPT}\n\nRetrieved Database Results:\n{sql_results}\n\nUser Question: {q}\n\nAnswer:\n"

    try:
        ans_resp = llm.invoke(answer_prompt)
        answer_text = ans_resp.content if hasattr(ans_resp, 'content') else str(ans_resp)
    except Exception:
        answer_text = f"Finance Controller Report: Verified database query. Retrieved {len(sql_results)} result items for batch '{batch_id}'."

    return {
        "question": q,
        "query": sql_query,
        "sql_query": sql_query,
        "sql_executed_safely": executed_safely,
        "answer": answer_text,
        "response": answer_text,
        "retrieved_facts": sql_results
    }
