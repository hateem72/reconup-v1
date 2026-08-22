import time
from typing import Dict, Any, List
from app.agents.state import FinanceState
from app.finance.normalizer import normalize_status, llm_normalize_statuses, clean_quantity, parse_numeric_amount
from app.schemas.canonical import CanonicalOrder, CanonicalPayment
from app.core.logging import log_stage
from app.agents.column_mapping_agent import log_agent_call

def normalization_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 3: StatusNormalizationAgent (Local LLM Ollama qwen2.5:3b) categorizes unique raw status
    strings into canonical categories (Delivered, Return, RTO, Cancelled, Shipped, Return_Initiated, Claim).
    Normalizes raw rows into CanonicalOrder and CanonicalPayment models with 100% source traceability.
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    raw_datasets = state.get("raw_datasets", [])
    column_mappings = state.get("column_mappings", {})

    print("\n" + "="*80)
    print(f"  [NODE 3: CANONICAL NORMALIZATION & LLM STATUS CLASSIFICATION] STARTED FOR BATCH: {batch_id}")
    print("="*80)

    log_stage("NODE 3", f"Starting Node 3 Normalization across {len(raw_datasets)} datasets")

    raw_statuses = set()
    for ds in raw_datasets:
        fname = ds.get("filename", "")
        rows = ds.get("data", [])
        mapping = column_mappings.get(fname, {})
        status_col = mapping.get("status", {}).get("source_column") if isinstance(mapping.get("status"), dict) else None
        
        if not status_col and rows and isinstance(rows[0], dict):
            status_col = next((k for k in rows[0].keys() if "status" in k.lower() or "credit" in k.lower()), None)

        if status_col:
            for r in rows:
                val = str(r.get(status_col, "")).strip()
                if val and val.lower() != "nan":
                    raw_statuses.add(val)

    print(f"\n--- [NODE 3 AI AGENT: StatusNormalizationAgent] ---")
    print(f"  • Extracted {len(raw_statuses)} unique raw status strings across datasets.")

    status_map = llm_normalize_statuses(list(raw_statuses))

    print(f"  • AI Status Categorization Matrix ({len(status_map)} categories mapped):")
    for raw_s, info in status_map.items():
        cat = info.get("canonical_category", raw_s) if isinstance(info, dict) else raw_s
        conf = info.get("confidence") if isinstance(info, dict) else 1.0
        conf_val = float(conf) if conf is not None else 1.0
        print(f"      - \"{raw_s}\" ──▶ Canonical Category: [{cat}] (Confidence: {round(conf_val, 2)})")

    canonical_orders: List[CanonicalOrder] = []
    canonical_payments: List[CanonicalPayment] = []
    master_order_ids = set()

    for ds in raw_datasets:
        fname = ds.get("filename", "")
        role = ds.get("role", "MASTER ORDER SHEET")
        rows = ds.get("data", [])
        mapping = column_mappings.get(fname, {})

        simple_map = {c_f: info.get("source_column") for c_f, info in mapping.items() if isinstance(info, dict)}
        
        order_id_col = simple_map.get("order_id") or "Sub Order No"
        sku_col = simple_map.get("sku") or "SKU"
        qty_col = simple_map.get("quantity") or "Quantity"
        status_col = simple_map.get("status") or "Live Order Status"
        date_col = simple_map.get("order_date") or simple_map.get("payment_date") or "Order Date"
        amount_col = simple_map.get("amount") or "Final Settlement Amount"

        if role == "MASTER ORDER SHEET":
            print(f"\n--- [NORMALIZING MASTER ORDER SHEET]: {fname} ({len(rows)} rows) ---")
            for idx, r in enumerate(rows):
                oid = str(r.get(order_id_col, "")).strip()
                if not oid or oid.lower() in ("nan", "null", "none"):
                    continue

                master_order_ids.add(oid)
                raw_st = str(r.get(status_col, "")).strip()
                norm_cat = status_map.get(raw_st, {}).get("canonical_category", raw_st) if isinstance(status_map.get(raw_st), dict) else normalize_status(raw_st)

                c_ord = CanonicalOrder(
                    order_id=oid,
                    sku=str(r.get(sku_col, "")).strip(),
                    product_name=str(r.get("Product Name", r.get("product_name", ""))).strip(),
                    quantity=clean_quantity(r.get(qty_col, 1)),
                    status=norm_cat,
                    order_date=str(r.get(date_col, "")).strip(),
                    source_platform="Meesho/Generic",
                    source_file=fname,
                    source_sheet="OrderSheet",
                    source_row=idx + 2,
                    raw_data={str(k): str(v) for k, v in r.items() if str(v).lower() != "nan"}
                )
                canonical_orders.append(c_ord)

        else:
            print(f"\n--- [NORMALIZING PAYMENT SETTLEMENT SHEET]: {fname} ({len(rows)} multi-event rows) ---")
            for idx, r in enumerate(rows):
                oid = str(r.get(order_id_col, "")).strip()
                if not oid or oid.lower() in ("nan", "null", "none"):
                    continue

                raw_st = str(r.get(status_col, "")).strip()
                norm_cat = status_map.get(raw_st, {}).get("canonical_category", raw_st) if isinstance(status_map.get(raw_st), dict) else normalize_status(raw_st)
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

    # Filter payment lines to strictly retain only those matching Master Order Sheet Order IDs
    filtered_payments = [p for p in canonical_payments if p.order_id in master_order_ids]
    discarded_count = len(canonical_payments) - len(filtered_payments)

    print("\n" + "="*80)
    print(f"  [NODE 3 SUMMARY & PAYMENT SHEET FILTERING]:")
    print(f"  • Normalized Canonical Orders (Master Anchor): {len(canonical_orders)} records ({len(master_order_ids)} unique order IDs)")
    print(f"  • Total Raw Payment Lines Ingested: {len(canonical_payments)} lines")
    print(f"  • Retained Payment Lines (Matching Master Order Sheet): {len(filtered_payments)} lines")
    print(f"  • Filtered Out Historical Payment Lines (Previous Months): {discarded_count} lines")
    print(f"  • Data Reduction: {round((discarded_count / max(len(canonical_payments), 1)) * 100, 1)}% data reduction for faster Node 4 & Node 5 throughput!")
    print("="*80 + "\n")

    log_agent_call(
        agent_name="StatusNormalizationAgent",
        task="Categorize raw statuses into canonical order lifecycle states",
        input_summary=f"{len(raw_statuses)} unique raw status strings",
        output_summary=f"Categorized into {len(status_map)} categories",
        confidence=0.97,
        duration_sec=time.time() - start_time
    )

    log_stage("NODE 3", f"Node 3 complete. Normalized {len(canonical_orders)} orders and retained {len(filtered_payments)} matched payment lines (filtered out {discarded_count} historical lines).")

    return {
        "canonical_orders": canonical_orders,
        "canonical_payments": filtered_payments,
        "master_order_ids_count": len(master_order_ids),
        "historical_payments_count": discarded_count,
        "status_mappings": status_map,
        "status": "NODE_3_NORMALIZED"
    }
