import json
from typing import Dict, Any, List
from app.agents.core.llm_factory import get_llm
from app.agents.core.prompts import SHEET_RELEVANCE_PROMPT
from app.core.logging import log_stage, log_agent_call
from app.finance.order_normalizer import parse_json_from_llm_text

class SheetRelevanceAgent:
    """
    Dedicated AI Agent: SheetRelevanceAgent (Node 1.5)
    Evaluates every discovered workbook sub-tab using Local LLM (qwen2.5:3b) to determine
    whether it is REQUIRED for order-level financial reconciliation or NOT_REQUIRED
    (summary tabs, GST reports, index sheets, ad cost notes, or empty disclaimers).
    """

    def __init__(self):
        self.llm = get_llm()

    def evaluate_sheet_relevance(self, raw_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("\n" + "="*80)
        print("  [NODE 1.5 AI AGENT: SheetRelevanceAgent] EXECUTION STARTED")
        print("="*80)
        
        log_stage("NODE 1.5", f"SheetRelevanceAgent evaluating {len(raw_datasets)} discovered sub-tabs via AI classification")
        
        retained_datasets = []
        dropped_datasets = []

        for idx, ds in enumerate(raw_datasets):
            fname = ds.get("filename", f"tab_{idx+1}")
            role = ds.get("role", "MASTER ORDER SHEET")
            rows = ds.get("data", [])
            row_cnt = len(rows)

            headers = []
            if rows and isinstance(rows[0], dict):
                headers = ds.get("exact_headers") or [str(k) for k in dict.fromkeys([k for r in rows[:10] for k in r.keys() if k != "id"])]

            print(f"\n--- [EVALUATING SUB-TAB #{idx+1}]: {fname} [{role}] ---")
            print(f"  • Dimensions: {row_cnt} rows x {len(headers)} columns")

            # 1. Zero-data empty disclaimer check
            if row_cnt == 0:
                verdict = "NOT_REQUIRED"
                rationale = "Empty sub-tab disclaimer with 0 data rows."
            else:
                # 2. Invoke Local LLM (qwen2.5:3b) with compact, anti-hallucination metadata payload
                try:
                    # Prepare lightweight sample row preview (capped to 35 chars per value to stay under 350 tokens)
                    sample_preview = {}
                    if rows and isinstance(rows[0], dict):
                        for k, v in list(rows[0].items())[:12]:
                            str_val = str(v).strip()
                            sample_preview[str(k)] = (str_val[:35] + "...") if len(str_val) > 35 else str_val

                    prompt = (
                        f"{SHEET_RELEVANCE_PROMPT}\n\n"
                        f"Sub-Tab Metadata:\n"
                        f"• Sub-Tab Name: {fname}\n"
                        f"• Declared Role: {role}\n"
                        f"• Total Data Rows: {row_cnt}\n"
                        f"• Total Column Count: {len(headers)}\n"
                        f"• Headers JSON: {json.dumps(headers)}\n"
                        f"• Sample Row Data: {json.dumps(sample_preview)}\n\n"
                        f"Evaluate whether this sheet contains line-item order transactions/settlements (REQUIRED) or summary/disclaimer data (NOT_REQUIRED):"
                    )

                    resp = self.llm.invoke(prompt)
                    res_text = getattr(resp, "content", str(resp))
                    parsed = parse_json_from_llm_text(res_text)

                    if parsed and isinstance(parsed, dict) and "verdict" in parsed:
                        verdict = str(parsed.get("verdict", "REQUIRED")).upper().strip()
                        rationale = str(parsed.get("rationale", "Evaluated by SheetRelevanceAgent Local LLM."))
                    else:
                        # Fallback heuristic if LLM JSON format is invalid
                        fname_lower = fname.lower()
                        if any(kw in fname_lower for kw in ["disclaimer", "ads cost", "referral", "index", "gst"]):
                            verdict = "NOT_REQUIRED"
                            rationale = f"Summary/disclaimer tab identified by sheet title '{fname}'."
                        else:
                            verdict = "REQUIRED"
                            rationale = "Order manifest or main transaction sheet containing order settlement lines."
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
