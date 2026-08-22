import React from 'react';
import { Grid, CheckCircle2, Bot, ArrowRight, ShieldCheck } from 'lucide-react';

export default function ColumnMappingView({ onNext }) {
  const mappings = [
    { canonical: 'order_id', source: 'Sub Order No', conf: '1.00', status: 'VALIDATED' },
    { canonical: 'amount', source: 'Final Settlement Amount', conf: '1.00', status: 'VALIDATED' },
    { canonical: 'status', source: 'Reason for Credit Entry / Live Order Status', conf: '0.98', status: 'VALIDATED' },
    { canonical: 'sku', source: 'Supplier SKU', conf: '0.99', status: 'VALIDATED' },
    { canonical: 'quantity', source: 'Quantity / Qty', conf: '1.00', status: 'VALIDATED' },
    { canonical: 'order_date', source: 'Order Date / Settlement Date', conf: '0.97', status: 'VALIDATED' }
  ];

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-white">Step 3: AI Column Mapping & Validation Matrix</h2>
            <p className="text-xs text-slate-400">
              Autonomous Agent <strong className="text-indigo-300">ColumnMappingAgent</strong> mapped headers using Local LLM <strong className="text-cyan-300">qwen2.5:3b</strong>
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          ⚡ Smart Schema Cache Hit (0s Latency)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/60">
              <th className="py-3 px-4">Canonical Target Field</th>
              <th className="py-3 px-4">Mapped Source Header</th>
              <th className="py-3 px-4 text-center">AI Confidence</th>
              <th className="py-3 px-4 text-right">Structural Guardrail</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {mappings.map((m, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40">
                <td className="py-3 px-4 font-bold text-cyan-400">{m.canonical}</td>
                <td className="py-3 px-4 text-white font-semibold">"{m.source}"</td>
                <td className="py-3 px-4 text-center text-emerald-400 font-bold">{m.conf}</td>
                <td className="py-3 px-4 text-right">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    ✓ {m.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-end pt-4 border-t border-slate-800">
        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-2 transition"
        >
          <span>Proceed to Step 4: Order Reconciliation Engine</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
