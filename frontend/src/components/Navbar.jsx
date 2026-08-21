import React from 'react';
import { ShieldCheck, Cpu, BookOpen, RefreshCw } from 'lucide-react';

export default function Navbar({ onOpenRules, onRunDemo, isProcessing }) {
  return (
    <header className="border-b border-gray-800 bg-[#0F172A]/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-xl tracking-tight text-white flex items-center gap-2">
              Agentic AI <span className="gradient-text">Finance Controller</span>
            </h1>
            <p className="text-xs text-gray-400">Track 04 — Books & Cash Reconciliation Engine</p>
          </div>
        </div>

        {/* Engine Badges & Actions */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 bg-gray-900/80 px-3 py-1.5 rounded-lg border border-gray-800 text-xs text-gray-300">
            <Cpu className="w-4 h-4 text-emerald-400" />
            <span>Deterministic Engine + LangGraph</span>
          </div>

          <button
            onClick={onOpenRules}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition"
          >
            <BookOpen className="w-4 h-4 text-indigo-400" />
            Rule Registry
          </button>

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-600/20 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
            {isProcessing ? 'Processing Batch...' : 'Run 100-Record Synthetic Demo'}
          </button>
        </div>
      </div>
    </header>
  );
}
