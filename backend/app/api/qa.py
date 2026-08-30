import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
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
executor = ThreadPoolExecutor(max_workers=4)

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

def run_llm_with_timeout(llm, prompt: str, timeout_sec: float = 6.0) -> str:
    """Executes LLM invoke with a hard timeout to prevent backend hanging."""
    try:
        future = executor.submit(llm.invoke, prompt)
        resp = future.result(timeout=timeout_sec)
        return resp.content if hasattr(resp, 'content') else str(resp)
    except Exception as e:
        return f"-- LLM Timeout/Error: {str(e)}"

@router.post("/qa")
def ask_finance_question(req: QARequest, db: Session = Depends(get_db)):
    repo = FinanceRepository(db)
    q = (req.query or req.question or "").strip()
    batch_id = req.batch_id or "batch_demo"
    q_lower = q.lower()
    
    llm = get_llm(temperature=0.0)
    
    # 1. Step 1: Text-to-SQL Query Generation with hard timeout safeguard
    system_prompt = TEXT_TO_SQL_SYSTEM_PROMPT.format(batch_id=batch_id)
    sql_prompt = f"{system_prompt}\n\nUser Question: {q}\n"

    raw_sql = run_llm_with_timeout(llm, sql_prompt, timeout_sec=6.0)
    sql_query = ""
    sql_results: List[Dict[str, Any]] = []
    executed_safely = False

    match = re.search(r'```sql\s*(.*?)\s*```', raw_sql, re.DOTALL | re.IGNORECASE)
    if match:
        sql_query = match.group(1).strip()
    elif "SELECT" in raw_sql.upper():
        sql_query = raw_sql.strip()

    # Filter sql_query placeholder tags
    sql_query = sql_query.replace("<order_id_snippet>", "1").replace("<query_snippet>", "1")

    if sql_query and is_safe_sql(sql_query):
        try:
            res = db.execute(text(sql_query))
            sql_results = [dict(r._mapping) for r in res.fetchall()[:25]]
            executed_safely = True
        except Exception as e:
            sql_query = f"-- SQL Execution Error: {str(e)}"

    # 2. Domain Keyword Fallbacks if SQL returns empty
    if not sql_results:
        # Fallback A: Return Cost / Return Payout queries
        if any(w in q_lower for w in ["return", "rto", "refund", "returned"]):
            ret_sql = """
            SELECT order_id, order_status, payment_status, payment_amount 
            FROM reconciliation_results 
            WHERE batch_id = :b_id AND (order_status IN ('Return', 'RTO', 'Return_Initiated') OR payment_status LIKE '%Return%' OR payment_status LIKE '%Deduction%')
            LIMIT 25
            """
            try:
                res = db.execute(text(ret_sql), {"b_id": batch_id})
                rows = [dict(r._mapping) for r in res.fetchall()]
                if rows:
                    sql_results = rows
                    tot_ret_amount = sum(r.get("payment_amount", 0.0) for r in rows)
                    sql_results.insert(0, {"summary": f"Total Return Orders: {len(rows)}", "total_return_amount_inr": round(tot_ret_amount, 2)})
                    sql_query = f"-- Return Domain Fallback Query\n{ret_sql}"
                    executed_safely = True
            except Exception:
                pass

    # 3. Fallback B: Order ID Fuzzy Search
    if not sql_results:
        id_matches = re.findall(r'[A-Za-z0-9_\-]{5,}', q)
        search_term = id_matches[0] if id_matches else ""
        if search_term:
            fuzzy_sql = """
            SELECT 
              o.order_id, o.sku, o.status AS order_status, o.dispatch_date,
              p.transaction_id, p.payment_date, p.settlement_amount, p.status AS payment_status,
              r.match_status, r.difference
            FROM orders o
            LEFT JOIN payments p ON o.order_id = p.order_id OR p.order_id LIKE '%' || o.order_id || '%' OR o.order_id LIKE '%' || p.order_id || '%'
            LEFT JOIN reconciliation_results r ON o.order_id = r.order_id
            WHERE o.order_id LIKE :term OR p.order_id LIKE :term OR o.sku LIKE :term
            LIMIT 10
            """
            try:
                res = db.execute(text(fuzzy_sql), {"term": f"%{search_term}%"})
                rows = [dict(r._mapping) for r in res.fetchall()]
                if rows:
                    sql_results = rows
                    sql_query = f"-- Order ID Fuzzy Search Fallback\n{fuzzy_sql}"
                    executed_safely = True
            except Exception:
                pass

    # 4. Fallback C: General Batch Overview
    if not sql_results:
        batch = repo.get_batch(batch_id)
        report = repo.get_latest_report(batch_id)
        exceptions = repo.get_exceptions(batch_id)
        rec_results = repo.get_reconciliation_results(batch_id)
        
        tot_orders = len(repo.get_canonical_orders(batch_id))
        matched_cnt = len([r for r in rec_results if r.match_status in ("EXACT_MATCH", "OVERPAID")])
        tot_payout = sum(r.payment_amount for r in rec_results)

        sql_results = [{
            "batch_id": batch_id,
            "status": batch.status if batch else "COMPLETED",
            "match_rate_pct": report.match_rate if report else 100.0,
            "total_orders_count": tot_orders,
            "matched_orders_count": matched_cnt,
            "total_net_payout_inr": round(tot_payout, 2),
            "unresolved_exceptions_count": len([e for e in exceptions if e.status == "PENDING"]),
            "pending_exceptions_sample": [
                {"order_id": e.order_id, "type": e.exception_type, "amount": e.amount}
                for e in exceptions if e.status == "PENDING"
            ][:5]
        }]

    # 5. Step 2: Answer Synthesis with Hard Timeout
    answer_prompt = f"{QA_ANSWER_SYNTHESIS_PROMPT}\n\nRetrieved Empirical Database Results:\n{sql_results}\n\nUser Question: {q}\n\nAnswer:\n"
    
    ans_text = run_llm_with_timeout(llm, answer_prompt, timeout_sec=6.0)
    if ans_text.startswith("-- LLM Timeout"):
        # Instant fallback response generation without stalling UI
        tot_p = sql_results[0].get("total_payout_inr") or sql_results[0].get("total_net_payout_inr") or 0.0
        ans_text = f"### Finance Analysis Response\nRetrieved empirical database facts for batch `{batch_id}`.\n\nQuery results summary: Found **{len(sql_results)}** matching records in SQLite database."

    return {
        "question": q,
        "query": sql_query,
        "sql_query": sql_query,
        "sql_executed_safely": executed_safely,
        "answer": ans_text,
        "response": ans_text,
        "retrieved_facts_count": len(sql_results),
        "retrieved_facts": sql_results
    }
