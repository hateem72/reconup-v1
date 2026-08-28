import json
from typing import Dict, Any, List
from app.agents.core.llm_factory import get_llm
from app.agents.core.prompts import SHEET_RELEVANCE_PROMPT
from app.core.logging import log_stage, log_agent_call
from app.finance.order_normalizer import parse_json_from_llm_text

class SheetRelevanceAgent:
    """
    Dedicated Autonomous AI Agent: SheetRelevanceAgent (Node 1.5)
    Evaluates EVERY discovered workbook sub-tab using Local LLM (qwen2.5:3b) semantic intelligence.
    NO hardcoded keyword lists or row-count shortcuts are used.
    Determines whether each sub-tab is REQUIRED for order-level financial reconciliation
    or NOT_REQUIRED (summary tabs, GST reports, index sheets, ad cost notes, or empty disclaimers).
    """

    def __init__(self):
        self.llm = get_llm()

    def evaluate_sheet_relevance(self, raw_datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        print("\n" + "="*80)
        print("  [NODE 1.5 AI AGENT: SheetRelevanceAgent] PURE AI EVALUATION STARTED")
        print("="*80)
        
        log_stage("NODE 1.5", f"SheetRelevanceAgent evaluating {len(raw_datasets)} sub-tabs via pure LLM semantic intelligence")
        
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

            # Prepare lightweight sample row preview (top 2 rows, capped to 35 chars per string value)
            sample_preview = []
            if rows:
                for sample_r in rows[:2]:
                    if isinstance(sample_r, dict):
                        row_dict = {}
                        for k, v in list(sample_r.items())[:15]:
                            str_val = str(v).strip()
                            row_dict[str(k)] = (str_val[:35] + "...") if len(str_val) > 35 else str_val
                        sample_preview.append(row_dict)

            # Construct pure LLM semantic evaluation prompt for this sub-tab
            prompt = (
                f"{SHEET_RELEVANCE_PROMPT}\n\n"
                f"Sub-Tab Metadata:\n"
                f"• Sub-Tab Name: {fname}\n"
                f"• Declared Role: {role}\n"
                f"• Total Data Rows: {row_cnt}\n"
                f"• Total Column Count: {len(headers)}\n"
                f"• Headers JSON: {json.dumps(headers)}\n"
                f"• Sample Row Data: {json.dumps(sample_preview)}\n\n"
                f"Classify whether this sub-tab is REQUIRED for line-item financial reconciliation or NOT_REQUIRED:"
            )

            try:
                resp = self.llm.invoke(prompt)
                res_text = getattr(resp, "content", str(resp))
                parsed = parse_json_from_llm_text(res_text)

                if parsed and isinstance(parsed, dict) and "verdict" in parsed:
                    verdict = str(parsed.get("verdict", "REQUIRED")).upper().strip()
                    rationale = str(parsed.get("rationale", "Evaluated by SheetRelevanceAgent Local LLM."))
                else:
                    verdict = "REQUIRED"
                    rationale = "LLM evaluation parsed as REQUIRED by default."
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
