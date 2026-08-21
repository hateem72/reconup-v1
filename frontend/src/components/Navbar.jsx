import React from 'react';
import { ShieldCheck, Cpu, BookOpen, RefreshCw, Activity, Terminal, DollarSign } from 'lucide-react';

export default function Navbar({ onOpenRules, onOpenCosts, onRunDemo, isProcessing, activeBatchId }) {
  return (
    <header className="border-b border-gray-800/80 bg-[#0B0F17]/90 backdrop-blur-xl sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center shadow-lg glow-blue">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-gray-900 pulse-dot"></span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-extrabold text-xl tracking-tight text-white">
                FINANCE <span className="gradient-text-blue">CONTROLLER</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-widest">
                AI Agentic Loop
              </span>
            </div>
            <p className="text-[11px] text-gray-400 font-medium">Multi-Source Reconciliation & Automated Governance Engine</p>
          </div>
        </div>

        {/* System Badges & Actions */}
        <div className="flex items-center gap-3">
          {activeBatchId && (
            <div className="hidden lg:flex items-center gap-2 bg-gray-900/90 px-3 py-1.5 rounded-xl border border-gray-800 text-xs">
              <Terminal className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-gray-400">Batch:</span>
              <span className="font-mono font-bold text-blue-400">{activeBatchId}</span>
            </div>
          )}

          <div className="hidden md:flex items-center gap-2 bg-emerald-500/10 px-3 py-1.5 rounded-xl border border-emerald-500/20 text-xs text-emerald-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400 pulse-dot" />
            <span className="font-medium">Deterministic Engine Active</span>
          </div>

          <button
            onClick={onOpenCosts}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-emerald-300 border border-emerald-500/30 transition shadow-sm hover:border-emerald-500/50"
          >
            <DollarSign className="w-4 h-4 text-emerald-400" />
            Set SKU Costs
          </button>

          <button
            onClick={onOpenRules}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-200 border border-gray-700/80 transition shadow-sm hover:border-gray-600"
          >
            <BookOpen className="w-4 h-4 text-indigo-400" />
            Rule Registry
          </button>

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-lg glow-blue transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isProcessing ? 'animate-spin' : ''}`} />
            {isProcessing ? 'Processing Batch...' : 'Run 100-Record Synthetic Demo'}
          </button>
        </div>
      </div>
    </header>
  );
}
