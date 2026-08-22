import time
from typing import Dict, Any
from app.agents.core.state import FinanceState
from app.finance.reconciliation import reconcile_canonical_records
from app.core.logging import log_stage
from app.agents.specialized.column_mapping_agent import log_agent_call

def reconciliation_node(state: FinanceState) -> Dict[str, Any]:
    """
    NODE 5: Executes deterministic reconciliation matching between Master Orders and Payment Settlement lines.
    Matches Master Order IDs against Payment Sheet Order IDs, aggregates multi-event payouts per order ID
    to compute Net Payout Amount, and returns complete 3-way reconciliation datasets.
    """
    start_time = time.time()
    batch_id = state.get("batch_id", "batch_demo")
    canonical_orders = state.get("canonical_orders", [])
    canonical_payments = state.get("canonical_payments", [])

    print("\n" + "="*80)
    print(f"  [NODE 5: DETERMINISTIC ORDER-PAYMENT RECONCILIATION] STARTED FOR BATCH: {batch_id}")
    print("="*80)

    log_stage("NODE 5", f"Starting Node 5 Reconciliation across {len(canonical_orders)} Master Orders and {len(canonical_payments)} Payment Lines")

    rec_res = reconcile_canonical_records(canonical_orders, canonical_payments)
    
    matched_items = rec_res.get("matched", [])
    missing_in_pmt = rec_res.get("missingInPayment", [])
    missing_in_ord = rec_res.get("missingInOrder", [])
    match_rate = rec_res.get("matchRate", 0.0)

    print(f"\n--- [NODE 5 RECONCILIATION MATCHING SUMMARY] ---")
    print(f"  • Master Order Sheet Anchors: {rec_res.get('totalOrders', 0)} orders")
    print(f"  • Total Payment Settlement Lines Ingested: {len(canonical_payments)} event lines")
    print(f"  • Matched Orders (Order Sheet ──▶ Payment Settlement): {len(matched_items)} orders")
    print(f"  • Orders Missing Payment (Unsettled): {len(missing_in_pmt)} orders")
    print(f"  • Historical Payment Lines (Previous Months): {len(missing_in_ord)} lines")
    print(f"  • Master Order Match Rate: {match_rate}%")
    print(f"  • Life-Cycle Totals: Delivered={rec_res.get('countDelivered', 0)}, Returns={rec_res.get('countReturns', 0)}, RTO={rec_res.get('countRTO', 0)}")

    if matched_items:
        print(f"\n  • Sample Matched Net Payout Aggregations (Top 3 Records):")
        for m in matched_items[:3]:
            print(f"      - Order [{m.get('orderId')}] ──▶ Status: {m.get('orderSheetStatus')} | Net Payout: ₹{m.get('totalPayment')} | Events: '{m.get('paymentStatuses')}'")

    print("\n" + "="*80)
    print(f"  [NODE 5 COMPLETE] Reconciliation verified ({len(matched_items)} matched, {len(missing_in_pmt)} missing payment).")
    print("="*80 + "\n")

    log_agent_call(
        agent_name="ReconciliationEngine",
        task="Match Master Order manifest against Payment Settlement events & aggregate net payouts",
        input_summary=f"{len(canonical_orders)} Master Orders vs {len(canonical_payments)} Payment Lines",
        output_summary=f"Matched {len(matched_items)} orders ({match_rate}% match rate)",
        confidence=1.0,
        duration_sec=time.time() - start_time
    )

    log_stage("NODE 5", f"Node 5 complete. Match Rate: {match_rate}%. Ready for Node 6 financial P&L calculation.")

    return {
        "reconciliation_results": rec_res,
        "match_rate": match_rate,
        "status": "NODE_5_RECONCILED"
    }
