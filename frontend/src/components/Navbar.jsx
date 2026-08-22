import React, { useState } from 'react';
import { ShieldCheck, BookOpen, RefreshCw, Activity, Terminal, DollarSign, RotateCcw, Trash2, AlertTriangle } from 'lucide-react';

export default function Navbar({ onOpenRules, onOpenCosts, onRunDemo, onHardReset, isProcessing, activeBatchId }) {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleConfirmReset = () => {
    setShowConfirm(false);
    onHardReset();
  };

  return (
    <>
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

            <button
              onClick={() => setShowConfirm(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition shadow-xs"
              title="Clear all session caches & start reconciliation fresh"
            >
              <RotateCcw className="w-3.5 h-3.5 text-rose-600" />
              Hard Reset
            </button>

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

      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-md p-6 border border-slate-200 rounded-2xl shadow-2xl bg-white text-center">
            <div className="w-12 h-12 rounded-2xl bg-rose-100 border border-rose-200 text-rose-600 flex items-center justify-center mx-auto mb-3">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h3 className="text-base font-extrabold text-slate-900">Confirm System Hard Reset?</h3>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed font-medium">
              This will clear all active batch records, uploaded orders, payments, reconciliation results, surfaced exceptions, and session caches from SQLite database and reset the UI to Step 1.
            </p>

            <div className="mt-6 flex items-center justify-center gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmReset}
                className="px-5 py-2.5 rounded-xl text-xs font-extrabold bg-rose-600 hover:bg-rose-700 text-white shadow-md flex items-center gap-2 transition"
              >
                <Trash2 className="w-4 h-4" />
                Yes, Hard Reset & Clear Cache
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
