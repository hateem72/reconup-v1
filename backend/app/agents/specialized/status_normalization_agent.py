import time
import pandas as pd
from typing import Dict, Any, List
from app.agents.core.state import FinanceState
from app.finance.normalizer import normalize_status, parse_numeric_amount, clean_quantity
from app.schemas.canonical import CanonicalOrder, CanonicalPayment
from app.core.logging import log_agent_call, log_stage

def llm_normalize_statuses(raw_statuses: List[str]) -> Dict[str, Any]:
    """Uses Ollama qwen2.5:3b to categorize unique raw status strings into canonical lifecycle states."""
    if not raw_statuses:
        return {}

    log_stage("AGENT", f"Invoking StatusNormalizationAgent (Local LLM) for {len(raw_statuses)} unique raw status strings")
    try:
        from app.agents.core.llm_factory import get_llm
        from app.agents.core.prompts import STATUS_NORMALIZATION_PROMPT
        from app.finance.order_normalizer import parse_json_from_llm_text

        llm = get_llm()
        prompt = f"{STATUS_NORMALIZATION_PROMPT}\n\nRaw Status Strings: {raw_statuses}\n\nRespond with valid JSON object mapping each raw status to its canonical category:"
        resp = llm.invoke(prompt)
        res_text = getattr(resp, "content", str(resp))
        parsed = parse_json_from_llm_text(res_text)
        if parsed and isinstance(parsed, dict):
            return parsed
    except Exception as e:
        log_stage("AGENT", f"LLM status normalization exception: {str(e)}", level="warn")

    # Fallback to deterministic status normalizer
    return {s: {"canonical_category": normalize_status(s), "confidence": 0.9} for s in raw_statuses}


def normalization_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 3: StatusNormalizationAgent categorizes unique raw status strings across all datasets
    and converts datasets into CanonicalOrder and CanonicalPayment domain models.
    All payment settlement payout amounts (Final Settlement Amount) are sourced exclusively
    from Payment Settlement Sheets.
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    raw_datasets = state.get("raw_datasets", [])
    column_mappings = state.get("column_mappings", {})

    raw_statuses = set()
    for ds in raw_datasets:
        fname = ds.get("filename", "")
        rows = ds.get("data", [])
        mapping = column_mappings.get(fname, {})
        status_col = mapping.get("status", {}).get("source_column") if isinstance(mapping.get("status"), dict) else None
        
        if not status_col and rows and isinstance(rows[0], dict):
            all_cols = ds.get("exact_headers") or list(dict.fromkeys([k for r in rows[:10] for k in r.keys() if k != "id"]))
            status_col = next((k for k in all_cols if "status" in k.lower() or "credit" in k.lower()), None)

        if status_col:
            for r in rows:
                val = str(r.get(status_col, "")).strip()
                if val and val.lower() != "nan":
                    raw_statuses.add(val)

    print(f"\n--- [NODE 3 AI AGENT: StatusNormalizationAgent] ---")
    print(f"  • Extracted {len(raw_statuses)} unique raw status strings across datasets.")
    log_stage("NODE 3", f"StatusNormalizationAgent extracted {len(raw_statuses)} unique raw status strings across datasets")

    status_map = llm_normalize_statuses(list(raw_statuses))

    canonical_orders: List[CanonicalOrder] = []
    canonical_payments: List[CanonicalPayment] = []
    master_order_ids = set()

    for idx, ds in enumerate(raw_datasets):
        fname = ds.get("filename", "")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        mapping = column_mappings.get(fname, {})
        
        if not rows or not isinstance(rows[0], dict):
            continue

        is_payment_sheet = "PAYMENT" in role.upper() or "SETTLEMENT" in role.upper() or "ORDER PAYMENTS" in fname.upper()

        order_id_col = mapping.get("order_id", {}).get("source_column", "Sub Order No")
        sku_col = mapping.get("sku", {}).get("source_column", "Supplier SKU")
        status_col = mapping.get("status", {}).get("source_column", "Live Order Status")
        qty_col = mapping.get("quantity", {}).get("source_column", "Quantity")
        date_col = mapping.get("order_date", {}).get("source_column") if not is_payment_sheet else mapping.get("payment_date", {}).get("source_column", "Payment Date")
        amount_col = mapping.get("amount", {}).get("source_column", "Final Settlement Amount") if is_payment_sheet else None

        if not is_payment_sheet:
            print(f"\n--- [NORMALIZING MASTER ORDER SHEET]: {fname} ({len(rows)} rows) ---")
            for idx, r in enumerate(rows):
                oid = str(r.get(order_id_col, "")).strip()
                if not oid or oid.lower() in ("nan", "null", "none"):
                    continue

                raw_st = str(r.get(status_col, "")).strip()
                norm_cat = status_map.get(raw_st, {}).get("canonical_category", raw_st) if isinstance(status_map.get(raw_st), dict) else normalize_status(raw_st)

                master_order_ids.add(oid)
                c_order = CanonicalOrder(
                    order_id=oid,
                    sku=str(r.get(sku_col, "")).strip(),
                    product_name=str(r.get("Product Name", r.get("product_name", ""))).strip(),
                    quantity=clean_quantity(r.get(qty_col, 1)),
                    status=norm_cat,
                    order_date=str(r.get(date_col, "")).strip(),
                    source_platform="Meesho/Generic",
                    source_file=fname,
                    source_sheet="MasterOrder",
                    source_row=idx + 2,
                    raw_data={str(k): str(v) for k, v in r.items() if str(v).lower() != "nan"}
                )
                canonical_orders.append(c_order)

        else:
            print(f"\n--- [NORMALIZING PAYMENT SETTLEMENT SHEET]: {fname} ({len(rows)} multi-event rows) ---")
            for idx, r in enumerate(rows):
                oid = str(r.get(order_id_col, "")).strip()
                if not oid or oid.lower() in ("nan", "null", "none"):
                    continue

                raw_st = str(r.get(status_col, "")).strip()
                norm_cat = status_map.get(raw_st, {}).get("canonical_category", raw_st) if isinstance(status_map.get(raw_st), dict) else normalize_status(raw_st)
                
                # Sourced exclusively from Payment Settlement Sheet (e.g. Final Settlement Amount)
                amt_val = parse_numeric_amount(r.get(amount_col, 0.0))

                c_pmt = CanonicalPayment(
                    transaction_id=str(r.get("Transaction ID", r.get("transaction_id", f"pmt-{idx+1}-{oid}"))).strip(),
                    order_id=oid,
                    settlement_amount=amt_val,
                    status=norm_cat,
                    quantity=clean_quantity(r.get(qty_col, 1)),
                    sku=str(r.get(sku_col, "")).strip(),
                    payment_date=str(r.get(date_col, "")).strip(),
                    source_platform="Meesho/Generic",
                    source_file=fname,
                    source_sheet="PaymentSheet",
                    source_row=idx + 2,
                    raw_data={str(k): str(v) for k, v in r.items() if str(v).lower() != "nan"}
                )
                canonical_payments.append(c_pmt)

    historical_payments_count = len([p for p in canonical_payments if p.order_id not in master_order_ids])

    log_stage("NODE 3", f"Normalized Master Orders: {len(canonical_orders)} records ({len(master_order_ids)} unique order IDs)")
    log_stage("NODE 3", f"Normalized Payment Settlement Lines: {len(canonical_payments)} lines from Payment Sheets (Sourced Final Settlement Amounts)")

    print("\n" + "="*80)
    print(f"  [NODE 3 SUMMARY & PAYMENT SHEET NORMALIZATION]:")
    print(f"  • Normalized Canonical Orders (Master Anchor): {len(canonical_orders)} records ({len(master_order_ids)} unique order IDs)")
    print(f"  • Total Payment Lines Normalized (Sourced Final Settlement Amounts): {len(canonical_payments)} lines")
    print(f"  • Historical Payment Lines (Previous Months): {historical_payments_count} lines")
    print("="*80 + "\n")

    log_agent_call(
        agent_name="StatusNormalizationAgent",
        task="Categorize raw statuses into canonical order lifecycle states",
        input_summary=f"{len(raw_statuses)} unique raw status strings",
        output_summary=f"Categorized into {len(status_map)} categories",
        confidence=0.97,
        duration_sec=time.time() - start_time
    )

    log_stage("NODE 3", f"Node 3 complete. Normalized {len(canonical_orders)} orders and {len(canonical_payments)} payment lines from Payment Sheets.")

    return {
        "canonical_orders": canonical_orders,
        "canonical_payments": canonical_payments,
        "master_order_ids_count": len(master_order_ids),
        "historical_payments_count": historical_payments_count,
        "status_mappings": status_map,
        "status": "NODE_3_NORMALIZED"
    }
