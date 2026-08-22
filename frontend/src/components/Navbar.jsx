import React from 'react';
import { Cpu, Play, RotateCcw, ShieldAlert, BookOpen, Layers } from 'lucide-react';

export default function Navbar({
  onRunDemo,
  onHardReset,
  isProcessing,
  activeBatchId
}) {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50 px-6 py-3.5 text-white">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo & Model Info */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-emerald-500 via-blue-600 to-indigo-600 p-0.5 shadow-lg shadow-blue-500/20">
            <div className="h-full w-full bg-slate-950 rounded-[14px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-emerald-400 animate-pulse" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold tracking-tight text-white flex items-center gap-1.5">
                FINANCE<span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">CONTROLLER.AI</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Track 04 Hackathon
              </span>
            </div>
            <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
              <span>Local LLM:</span>
              <span className="text-cyan-400 font-mono font-semibold">Ollama qwen2.5:3b</span>
              <span className="text-slate-600">•</span>
              <span>Deterministic Reconciliation Engine</span>
            </p>
          </div>
        </div>

        {/* Action Controls & Demo Buttons */}
        <div className="flex items-center gap-3">
          {activeBatchId && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
              <span>Batch:</span>
              <span className="text-emerald-400 font-bold">{activeBatchId}</span>
            </div>
          )}

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Synthetic Demo</span>
          </button>

          <button
            onClick={onHardReset}
            disabled={isProcessing}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center gap-1.5 transition disabled:opacity-50"
            title="Clear all database batches & reset pipeline"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Hard Reset</span>
          </button>
        </div>
      </div>
    </header>
  );
}
