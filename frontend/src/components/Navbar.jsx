import React from 'react';
import { ShieldCheck, BookOpen, RefreshCw, Activity, Terminal, DollarSign } from 'lucide-react';

export default function Navbar({ onOpenRules, onOpenCosts, onRunDemo, isProcessing, activeBatchId }) {
  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-blue-700 flex items-center justify-center shadow-md">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-white pulse-dot"></span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-xl tracking-tight text-slate-900">
                FINANCE <span className="gradient-text-blue">CONTROLLER</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-700 border border-blue-200 uppercase tracking-widest">
                AI Agentic Loop
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium">Multi-Source Settlement Reconciliation & Governance Platform</p>
          </div>
        </div>

        {/* System Actions & Status */}
        <div className="flex items-center gap-3">
          {activeBatchId && (
            <div className="hidden lg:flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 text-xs">
              <Terminal className="w-3.5 h-3.5 text-blue-600" />
              <span className="text-slate-500">Batch:</span>
              <span className="font-mono font-bold text-blue-700">{activeBatchId}</span>
            </div>
          )}

          <div className="hidden md:flex items-center gap-2 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200 text-xs text-emerald-800 font-semibold">
            <Activity className="w-3.5 h-3.5 text-emerald-600 pulse-dot" />
            <span>Deterministic Engine Active</span>
          </div>

          <button
            onClick={onOpenCosts}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 transition shadow-xs"
          >
            <DollarSign className="w-4 h-4 text-emerald-600" />
            Set SKU Costs
          </button>

          <button
            onClick={onOpenRules}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 transition shadow-xs"
          >
            <BookOpen className="w-4 h-4 text-indigo-600" />
            Rule Registry
          </button>

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-md transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
            {isProcessing ? 'Processing Batch...' : 'Run 100-Record Synthetic Demo'}
          </button>
        </div>
      </div>
    </header>
  );
}
