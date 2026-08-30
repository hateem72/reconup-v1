import React from 'react';
import { Cpu, Play, RotateCcw } from 'lucide-react';

export default function Navbar({
  onRunDemo,
  onHardReset,
  isProcessing,
  activeBatchId
}) {
  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur-xl sticky top-0 z-50 px-6 py-3.5 text-slate-900 shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo & Model Info */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-emerald-500 via-blue-600 to-indigo-600 p-0.5 shadow-md shadow-blue-500/10">
            <div className="h-full w-full bg-white rounded-[14px] flex items-center justify-center">
              <Cpu className="w-5 h-5 text-emerald-600" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight text-slate-900 flex items-center gap-0.5">
                Recon<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Up</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-blue-50 text-blue-700 border border-blue-200">
                Track 04 Hackathon
              </span>
            </div>
            <p className="text-[11px] text-slate-500 flex items-center gap-1.5 font-medium">
              <span>Local LLM:</span>
              <span className="text-blue-700 font-mono font-bold">Ollama qwen2.5:3b</span>
              <span className="text-slate-300">•</span>
              <span>Deterministic Reconciliation Engine</span>
            </p>
          </div>
        </div>

        {/* Action Controls & Demo Buttons */}
        <div className="flex items-center gap-3">
          {activeBatchId && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 border border-slate-200 text-xs font-mono text-slate-700">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
              <span>Batch:</span>
              <span className="text-blue-700 font-bold">{activeBatchId}</span>
            </div>
          )}

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 flex items-center gap-2 transition disabled:opacity-50 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Synthetic Demo</span>
          </button>

          <button
            onClick={onHardReset}
            disabled={isProcessing}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 flex items-center gap-1.5 transition disabled:opacity-50 cursor-pointer"
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
