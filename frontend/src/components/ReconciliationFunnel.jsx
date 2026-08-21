import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle, Layers } from 'lucide-react';

export default function ReconciliationFunnel({ reconciliation }) {
  if (!reconciliation) return null;

  const total = reconciliation.total_records || 1;
  const matched = reconciliation.matched_count || 0;
  const missingPayment = reconciliation.missing_payment_count || 0;
  const missingOrder = reconciliation.missing_order_count || 0;

  const matchedPct = Math.min(100, Math.round((matched / total) * 100));
  const missingPaymentPct = Math.min(100, Math.round((missingPayment / total) * 100));
  const missingOrderPct = Math.min(100, Math.round((missingOrder / total) * 100));

  return (
    <div className="glass-panel p-5 mb-8 border border-slate-200 shadow-soft bg-white">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-600" />
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-700">
            Reconciliation Funnel Distribution
          </h3>
        </div>
        <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
          Match Rate: {reconciliation.match_rate}%
        </span>
      </div>

      {/* Progress Bar Container */}
      <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex border border-slate-200 mb-4">
        <div
          style={{ width: `${matchedPct}%` }}
          className="bg-emerald-500 h-full transition-all duration-700"
          title={`Matched: ${matched}`}
        />
        <div
          style={{ width: `${missingPaymentPct}%` }}
          className="bg-amber-500 h-full transition-all duration-700"
          title={`Missing Payment: ${missingPayment}`}
        />
        <div
          style={{ width: `${missingOrderPct}%` }}
          className="bg-rose-500 h-full transition-all duration-700"
          title={`Missing Order: ${missingOrder}`}
        />
      </div>

      {/* Funnel Stat Chips */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50/70 border border-emerald-200">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span className="text-emerald-950 font-bold">Matched</span>
          </div>
          <div className="font-mono font-bold text-emerald-700">{matched} <span className="text-[10px] text-slate-500">({matchedPct}%)</span></div>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl bg-amber-50/70 border border-amber-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span className="text-amber-950 font-bold">Missing Payment</span>
          </div>
          <div className="font-mono font-bold text-amber-700">{missingPayment} <span className="text-[10px] text-slate-500">({missingPaymentPct}%)</span></div>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl bg-rose-50/70 border border-rose-200">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-rose-600" />
            <span className="text-rose-950 font-bold">Missing Order</span>
          </div>
          <div className="font-mono font-bold text-rose-700">{missingOrder} <span className="text-[10px] text-slate-500">({missingOrderPct}%)</span></div>
        </div>
      </div>
    </div>
  );
}
