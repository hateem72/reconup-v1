import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Shield, RefreshCw, Trash2, CheckCircle2 } from 'lucide-react';

export default function TerminalConsole({ batchId, isProcessing }) {
  const [logs, setLogs] = useState([
    { timestamp: new Date().toLocaleTimeString(), stage: 'SYSTEM', text: 'Reconciliation Controller Engine Ready. Waiting for file ingestion...' }
  ]);
  const [autoScroll, setAutoScroll] = useState(true);
  const logEndRef = useRef(null);

  useEffect(() => {
    if (batchId) {
      addLog('BATCH', `Started batch session: ${batchId}`);
      addLog('PROFILER', 'Discovering uploaded order and payment settlement sheets...');
      setTimeout(() => addLog('VALIDATOR', 'Validating column uniqueness (order_id uniqueness > 80%)...'), 300);
      setTimeout(() => addLog('RECONCILER', 'Executing multi-source order-to-settlement reconciliation matching...'), 700);
      setTimeout(() => addLog('GOVERNANCE', 'Surfacing reconciliation discrepancies & unknown deduction rules for human review...'), 1200);
    }
  }, [batchId]);

  useEffect(() => {
    if (autoScroll) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const addLog = (stage, text) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      stage,
      text
    }]);
  };

  const getStageColor = (stage) => {
    switch (stage) {
      case 'BATCH': return 'text-blue-600 font-bold';
      case 'PROFILER': return 'text-indigo-600 font-bold';
      case 'VALIDATOR': return 'text-purple-600 font-bold';
      case 'RECONCILER': return 'text-emerald-600 font-bold';
      case 'GOVERNANCE': return 'text-amber-600 font-bold';
      case 'ERROR': return 'text-rose-600 font-bold';
      default: return 'text-slate-500';
    }
  };

  return (
    <div className="glass-panel p-5 mb-8 border border-slate-300 bg-slate-900 text-slate-100 shadow-lg rounded-2xl">
      {/* Console Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-mono font-extrabold text-white flex items-center gap-2">
              RECONCILIATION PROCESS MONITORING CONSOLE
            </h3>
            <p className="text-[10px] text-slate-400 font-mono">Real-time terminal execution output ([PROFILER], [MAPPING], [RECONCILER], [GOVERNANCE])</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {isProcessing && (
            <span className="flex items-center gap-1.5 text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/20">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Processing Pipeline...
            </span>
          )}
          <button
            onClick={() => setLogs([])}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            title="Clear Console Logs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Output Area */}
      <div className="mt-3 h-48 overflow-y-auto font-mono text-xs space-y-1.5 pr-2 bg-slate-950/80 p-3.5 rounded-xl border border-slate-800/80">
        {logs.map((log, idx) => (
          <div key={idx} className="flex items-start gap-2 leading-relaxed">
            <span className="text-slate-500 text-[10px] shrink-0">[{log.timestamp}]</span>
            <span className={`text-[10px] uppercase px-1.5 py-0.2 rounded bg-slate-800 border border-slate-700 ${getStageColor(log.stage)}`}>
              [{log.stage}]
            </span>
            <span className="text-slate-200 font-sans">{log.text}</span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
