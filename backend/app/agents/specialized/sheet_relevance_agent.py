import json
from typing import Dict, Any, List
from app.agents.core.llm_factory import get_llm
from app.agents.core.prompts import SHEET_RELEVANCE_PROMPT
from app.core.logging import log_stage

class SheetRelevanceAgent:
    """
    Dedicated AI Agent: SheetRelevanceAgent (Node 1.5)
    Evaluates every discovered workbook sub-tab to determine whether it is REQUIRED for
    financial order reconciliation or NOT_REQUIRED (summary tabs / disclaimers).
    """

    def __init__(self):
        self.llm = get_llm()

    def evaluate_sheet_relevance(self, raw_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("\n" + "="*80)
        print("  [NODE 1.5 AI AGENT: SheetRelevanceAgent] EXECUTION STARTED")
        print("="*80)
        
        log_stage("NODE 1.5", f"SheetRelevanceAgent evaluating {len(raw_datasets)} discovered sub-tabs")
        
        retained_datasets = []
        dropped_datasets = []

        SUMMARY_KEYWORDS = ["ads cost", "referral", "disclaimer", "compensation and recovery", "reward id"]

        for idx, ds in enumerate(raw_datasets):
            fname = ds.get("filename", f"tab_{idx+1}")
            role = ds.get("role", "MASTER ORDER SHEET")
            rows = ds.get("data", [])
            row_cnt = len(rows)

            headers = []
            if rows and isinstance(rows[0], dict):
                headers = [str(k) for k in rows[0].keys() if k != "id"]

            fname_lower = fname.lower()
            
            is_master_order = "order" in role.lower() or "manifest" in fname_lower or "master" in fname_lower
            is_payment_main = "payment" in role.lower() or "settlement" in role.lower() or "order payments" in fname_lower
            is_explicit_summary = any(k in fname_lower for k in SUMMARY_KEYWORDS)

            print(f"\n--- [EVALUATING SUB-TAB #{idx+1}]: {fname} [{role}] ---")
            print(f"  • Dimensions: {row_cnt} rows x {len(headers)} columns")

            if is_master_order or (is_payment_main and not is_explicit_summary) or row_cnt > 10:
                verdict = "REQUIRED"
                rationale = "Master Order Manifest or Payment Settlement Sheet containing essential order transactions."
            elif row_cnt == 0:
                verdict = "NOT_REQUIRED"
                rationale = "Empty sub-tab disclaimer with 0 data rows."
            elif is_explicit_summary and len(headers) < 4 and row_cnt <= 5:
                verdict = "NOT_REQUIRED"
                rationale = f"Summary note tab '{fname}' containing non-order ad expenses or promotional notes."
            else:
                try:
                    prompt = f"""{SHEET_RELEVANCE_PROMPT}

Sub-Tab Name: {fname}
Declared Role: {role}
Row Count: {row_cnt}
Headers: {headers[:10]}
Sample Row: {rows[0] if rows else {}}

Evaluate relevance now:"""
                    resp = self.llm.invoke(prompt)
                    clean_text = resp.strip()
                    if "```json" in clean_text:
                        clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                    parsed = json.loads(clean_text)
                    verdict = parsed.get("verdict", "REQUIRED").upper()
                    rationale = parsed.get("rationale", "Evaluated by local LLM.")
                except Exception as e:
                    verdict = "REQUIRED"
                    rationale = f"LLM evaluation fallback to REQUIRED: {str(e)}"

            if verdict == "REQUIRED":
                retained_datasets.append(ds)
                print(f"  ✅ [DECISION]: RETAINED SUB-TAB")
                print(f"  • Rationale: {rationale}")
                log_stage("NODE 1.5", f"✅ Sub-Tab '{fname}': RETAINED ──▶ {rationale}")
            else:
                dropped_datasets.append({"filename": fname, "role": role, "row_count": row_cnt, "rationale": rationale})
                print(f"  🗑️ [DECISION]: DROPPED SUB-TAB (Summary/Disclaimer)")
                print(f"  • Rationale: {rationale}")
                log_stage("NODE 1.5", f"🗑️ Sub-Tab '{fname}': DROPPED ──▶ {rationale}")

        print("\n" + "="*80)
        print(f"  [NODE 1.5 COMPLETE] Retained {len(retained_datasets)} essential transaction sheets. Dropped {len(dropped_datasets)} summary sub-tabs.")
        print("="*80 + "\n")

        log_stage("NODE 1.5", f"Node 1.5 complete. Retained {len(retained_datasets)} transaction sheets, dropped {len(dropped_datasets)} summary sub-tabs.")

        return {
            "retained_datasets": retained_datasets,
            "dropped_datasets": dropped_datasets
        }
