import time
import json
from typing import List, Dict, Any
from app.core.logging import log_stage

class SheetRelevanceAgent:
    """
    Dedicated AI Agent for evaluating spreadsheet sub-tab metadata.
    Determines whether a sub-tab is REQUIRED (essential transaction dataset)
    or NOT_REQUIRED (non-essential summary/disclaimer tab).
    """

    def evaluate_sheet_relevance(self, raw_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        
        print("\n" + "="*80)
        print("  [AI AGENT: SheetRelevanceAgent] EVALUATING SUB-TAB RELEVANCE")
        print("="*80)

        log_stage("AGENT", f"SheetRelevanceAgent evaluating {len(raw_datasets)} sub-tabs")

        retained_datasets = []
        dropped_datasets = []

        NON_ESSENTIAL_KEYWORDS = ["ads cost", "referral", "disclaimer", "compensation and recovery", "reward id"]

        for idx, ds in enumerate(raw_datasets):
            fname = ds.get("filename", f"file_{idx+1}")
            role = ds.get("role", "MASTER ORDER SHEET")
            rows = ds.get("data", [])
            
            headers = [str(k) for k in rows[0].keys() if k != "id"] if rows and isinstance(rows[0], dict) else []
            row_cnt = len(rows)

            # Deterministic checks for Master Orders, Order Payment Settlements, vs Non-Essential Sub-Tabs
            is_master_order = role == "MASTER ORDER SHEET" or ("order" in fname.lower() and "payment" not in fname.lower())
            is_order_payment_settlement = "order payments" in fname.lower() or ("payment" in role.upper() and row_cnt > 5)
            has_transaction_headers = any(h_kw in str(headers).lower() for h_kw in ["sub order no", "final settlement amount", "live order status", "order date", "supplier sku", "amount"])

            is_empty_or_disclaimer = row_cnt == 0 or "disclaimer" in fname.lower()
            is_small_summary_tab = (row_cnt <= 5 and len(headers) < 4 and any(k in fname.lower() for k in NON_ESSENTIAL_KEYWORDS))

            verdict = "REQUIRED"
            rationale = "Transaction settlement or manifest dataset"

            if is_master_order or is_order_payment_settlement or has_transaction_headers:
                verdict = "REQUIRED"
                rationale = "Master Order Manifest or Payment Settlement Sheet containing order transactions"
            elif is_empty_or_disclaimer or is_small_summary_tab:
                verdict = "NOT_REQUIRED"
                rationale = f"Non-transactional summary/disclaimer tab ({row_cnt} rows, {len(headers)} cols)"
            else:
                try:
                    from app.agents.llm_factory import get_llm
                    from app.agents.prompts import SHEET_RELEVANCE_PROMPT
                    from app.finance.order_normalizer import parse_json_from_llm_text
                    
                    llm = get_llm()
                    prompt_input = (
                        f"{SHEET_RELEVANCE_PROMPT}\n\n"
                        f"Sub-Tab Name: {fname}\n"
                        f"Designated Role: {role}\n"
                        f"Row Count: {row_cnt}\n"
                        f"Header Columns: {headers[:10]}\n\n"
                        f"Respond with valid JSON mapping dictionary:"
                    )
                    res = llm.invoke(prompt_input)
                    res_text = getattr(res, "content", str(res))
                    parsed = parse_json_from_llm_text(res_text)
                    if parsed and "verdict" in parsed:
                        verdict = parsed.get("verdict", "REQUIRED").upper()
                        rationale = parsed.get("rationale", rationale)
                except Exception:
                    verdict = "REQUIRED"

            if verdict == "REQUIRED":
                retained_datasets.append(ds)
                print(f"  • \"{fname}\" ({len(headers)} cols, {row_cnt} rows)")
                print(f"    └─ AI Verdict: [REQUIRED] ({rationale}) ──▶ RETAINED ✓")
            else:
                dropped_datasets.append(ds)
                print(f"  • \"{fname}\" ({len(headers)} cols, {row_cnt} rows)")
                print(f"    └─ AI Verdict: [NOT_REQUIRED] ({rationale}) ──▶ DROPPED ✂️")

        print("\n" + "="*80)
        print(f"  [SheetRelevanceAgent RELEVANCE SUMMARY]:")
        print(f"  • Total Sub-Tabs Inspected: {len(raw_datasets)}")
        print(f"  • Retained Essential Transaction Sheets: {len(retained_datasets)}")
        print(f"  • Dropped Non-Essential Summary/Disclaimer Tabs: {len(dropped_datasets)}")
        print(f"  • Performance Optimization: {round((len(dropped_datasets)/max(len(raw_datasets), 1))*100, 1)}% noise reduction for Node 2!")
        print("="*80 + "\n")

        duration_sec = time.time() - start_time
        
        log_stage("AGENT", f"Agent: SheetRelevanceAgent | Task: Filter non-essential summary sub-tabs | Input: {len(raw_datasets)} tabs | Output: Retained {len(retained_datasets)} | Duration: {round(duration_sec, 3)}s | Status: SUCCESS")

        return {
            "retained_datasets": retained_datasets,
            "dropped_datasets": dropped_datasets,
            "duration_sec": duration_sec
        }
