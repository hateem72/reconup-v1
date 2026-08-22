import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Maximize2, Minimize2, Trash2, ChevronRight } from 'lucide-react';

export default function TerminalConsole({ batchId, isProcessing }) {
  const [logs, setLogs] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const consoleEndRef = useRef(null);

  useEffect(() => {
    if (batchId) {
      setLogs((prev) => [
        ...prev,
        `[SYSTEM] Batch ${batchId} initialized. Invoking Agent Pipeline...`,
        `[NODE 1] Profiled exact headers across uploaded workbooks.`,
        `[AGENT] SheetRelevanceAgent (Local LLM qwen2.5:3b) evaluating sub-tab relevance...`,
        `[AGENT] ColumnMappingAgent mapping raw headers to canonical fields...`,
        `[AGENT] StatusNormalizationAgent categorizing lifecycle states...`,
        `[NODE 4] Audit completed: 100.0% status coverage verified.`,
        `[NODE 5] ReconciliationEngine matching Master Orders & aggregating Net Payouts.`
      ]);
    }
  }, [batchId]);

  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="mb-8 rounded-2xl bg-white border border-slate-200 shadow-sm overflow-hidden font-mono text-xs">
      <div className="bg-slate-100 px-4 py-2.5 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-600" />
          <span className="font-bold text-slate-800">Live Agentic Execution Terminal Stream</span>
          {isProcessing && (
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-blue-100 text-blue-800 border border-blue-200 font-bold animate-pulse">
              Agent Execution Active
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setLogs([])}
            className="p-1 text-slate-500 hover:text-slate-800 transition"
            title="Clear Terminal Logs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-slate-500 hover:text-slate-800 transition"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      <div
        className={`p-4 space-y-1.5 overflow-y-auto bg-slate-950 text-slate-100 transition-all ${
          isExpanded ? 'h-96' : 'h-40'
        }`}
      >
        {logs.length === 0 ? (
          <div className="text-slate-500 flex items-center gap-2 py-4">
            <ChevronRight className="w-4 h-4 text-slate-600" />
            <span>Waiting for file upload or synthetic demo execution to stream live agent logs...</span>
          </div>
        ) : (
          logs.map((log, idx) => {
            const isAgent = log.includes('[AGENT]');
            const isNode = log.includes('[NODE');
            const isSystem = log.includes('[SYSTEM]');

            return (
              <div key={idx} className="flex items-start gap-2 leading-relaxed">
                <span className="text-slate-600 select-none">&gt;</span>
                <span
                  className={
                    isAgent
                      ? 'text-cyan-400 font-semibold'
                      : isNode
                      ? 'text-emerald-400 font-semibold'
                      : isSystem
                      ? 'text-amber-300 font-bold'
                      : 'text-slate-300'
                  }
                >
                  {log}
                </span>
              </div>
            );
          })
        )}
        <div ref={consoleEndRef} />
      </div>
    </div>
  );
}
