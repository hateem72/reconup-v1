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
    <div className="glass-panel p-5 mb-8 border border-gray-800">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-blue-400" />
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-gray-300">
            Reconciliation Funnel Distribution
          </h3>
        </div>
        <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
          Match Rate: {reconciliation.match_rate}%
        </span>
      </div>

      {/* Progress Bar Container */}
      <div className="w-full h-3 bg-gray-900 rounded-full overflow-hidden flex border border-gray-800 mb-4">
        <div
          style={{ width: `${matchedPct}%` }}
          className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-700"
          title={`Matched: ${matched}`}
        />
        <div
          style={{ width: `${missingPaymentPct}%` }}
          className="bg-gradient-to-r from-amber-500 to-orange-400 h-full transition-all duration-700"
          title={`Missing Payment: ${missingPayment}`}
        />
        <div
          style={{ width: `${missingOrderPct}%` }}
          className="bg-gradient-to-r from-rose-500 to-red-400 h-full transition-all duration-700"
          title={`Missing Order: ${missingOrder}`}
        />
      </div>

      {/* Funnel Stat Chips */}
      <div className="grid grid-cols-3 gap-3 text-xs">
        <div className="flex items-center justify-between p-2.5 rounded-xl bg-emerald-500/5 border border-emerald-500/15">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-gray-300 font-medium">Matched</span>
          </div>
          <div className="font-mono font-bold text-emerald-400">{matched} <span className="text-[10px] text-gray-500">({matchedPct}%)</span></div>
        </div>

        <div className="flex items-center justify-between p-2.5 rounded-xl bg-amber-500/5 border border-amber-500/15">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span className="text-gray-300 font-medium">Missing Payment</span>
          </div>
          <div className="font-mono font-bold text-amber-400">{missingPayment} <span className="text-[10px] text-gray-500">({missingPaymentPct}%)</span></div>
        </div>

        <div className="flex items-center justify-between p-2.5 rounded-xl bg-rose-500/5 border border-rose-500/15">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-rose-400" />
            <span className="text-gray-300 font-medium">Missing Order</span>
          </div>
          <div className="font-mono font-bold text-rose-400">{missingOrder} <span className="text-[10px] text-gray-500">({missingOrderPct}%)</span></div>
        </div>
      </div>
    </div>
  );
}
