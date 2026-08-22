import React from 'react';
import { Filter, CheckCircle2, XCircle, FileSpreadsheet, Bot, ArrowRight } from 'lucide-react';

export default function SheetDiscoveryView({ onNext }) {
  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 border border-blue-200">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 2: AI Sheet Relevance Evaluation</h2>
            <p className="text-xs text-slate-500 font-medium">
              Autonomous Agent <strong className="text-blue-700">SheetRelevanceAgent</strong> evaluates workbooks & drops non-essential tabs
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
          75% Noise Reduction Active
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl bg-slate-50 border border-emerald-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-emerald-800 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Retained Essential Transaction Sheets
            </span>
            <span className="text-xs font-mono text-emerald-700 font-bold">RETAINED ✓</span>
          </div>
          <p className="text-xs text-slate-600 font-medium">
            Contains order placement anchors, payment settlement payouts, SKU transaction lines, or status records.
          </p>
          <div className="p-3 rounded-lg bg-white border border-slate-200 text-xs font-mono space-y-1.5 text-slate-700 font-semibold shadow-xs">
            <div>• Master Order Manifest (1,947 rows x 13 cols)</div>
            <div>• Payment Settlement Sheet [Order Payments] (1,230 rows x 27 cols)</div>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 border border-rose-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-rose-800 flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-600" />
              Dropped Non-Essential Summary Sub-Tabs
            </span>
            <span className="text-xs font-mono text-rose-700 font-bold">DROPPED ✂️</span>
          </div>
          <p className="text-xs text-slate-600 font-medium">
            Ad cost summaries, referral text notes, disclaimer headers, or empty tabs without order transaction records.
          </p>
          <div className="p-3 rounded-lg bg-white border border-slate-200 text-xs font-mono space-y-1.5 text-slate-500 shadow-xs">
            <div>• Payment Settlement Sheet [Ads Cost] (2 rows x 3 cols)</div>
            <div>• Payment Settlement Sheet [Disclaimer] (0 rows x 1 col)</div>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4 border-t border-slate-200">
        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2 transition"
        >
          <span>Proceed to Step 3: LLM Mapping Matrix</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
