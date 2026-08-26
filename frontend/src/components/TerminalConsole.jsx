import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Maximize2, Minimize2, Trash2, ChevronRight, RefreshCw, ArrowDown } from 'lucide-react';

export default function TerminalConsole({ batchId, isProcessing }) {
  const [logs, setLogs] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const terminalContainerRef = useRef(null);

  useEffect(() => {
    if (!batchId) return;

    const fetchLogs = async () => {
      try {
        const res = await fetch(`/api/batches/${batchId}/logs`);
        if (res.ok) {
          const data = await res.json();
          if (data.logs && data.logs.length > 0) {
            const formatted = data.logs.map(
              (l) => `[${l.stage || 'STAGE'}] ${l.description}`
            );
            setLogs(formatted);
          }
        }
      } catch (err) {
        console.error("Error fetching audit logs:", err);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 1500);
    return () => clearInterval(interval);
  }, [batchId]);

  // Handle user scroll detection
  const handleScroll = () => {
    if (terminalContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = terminalContainerRef.current;
      // If user has scrolled up by more than 40px, pause auto-scroll so they can read previous logs
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 40;
      setAutoScroll(isAtBottom);
    }
  };

  useEffect(() => {
    if (autoScroll && terminalContainerRef.current) {
      terminalContainerRef.current.scrollTop = terminalContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const scrollToBottom = () => {
    if (terminalContainerRef.current) {
      terminalContainerRef.current.scrollTop = terminalContainerRef.current.scrollHeight;
      setAutoScroll(true);
    }
  };

  return (
    <div className="mb-8 rounded-2xl bg-white border border-slate-200 shadow-xs overflow-hidden font-mono text-xs relative">
      <div className="bg-slate-100 px-4 py-2.5 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-blue-600" />
          <span className="font-bold text-slate-800">Live Agentic Audit Log Terminal</span>
          {isProcessing ? (
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-blue-100 text-blue-800 border border-blue-200 font-bold flex items-center gap-1 animate-pulse">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Real-time Polling
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold">
              ✓ Synced
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
        ref={terminalContainerRef}
        onScroll={handleScroll}
        className={`p-4 space-y-1.5 overflow-y-auto bg-slate-950 text-slate-100 transition-all ${
          isExpanded ? 'h-96' : 'h-48'
        }`}
      >
        {logs.length === 0 ? (
          <div className="text-slate-500 flex items-center gap-2 py-4">
            <ChevronRight className="w-4 h-4 text-slate-600" />
            <span>Waiting for file upload or synthetic demo execution to stream live agent logs...</span>
          </div>
        ) : (
          logs.map((log, idx) => {
            const isAgent = log.includes('AGENT') || log.includes('RELEVANCE') || log.includes('MAPPING');
            const isNode = log.includes('NODE') || log.includes('STAGE_COMPLETE');

            return (
              <div key={idx} className="flex items-start gap-2 leading-relaxed">
                <span className="text-slate-600 select-none">&gt;</span>
                <span
                  className={
                    isAgent
                      ? 'text-cyan-400 font-semibold'
                      : isNode
                      ? 'text-emerald-400 font-semibold'
                      : 'text-slate-200'
                  }
                >
                  {log}
                </span>
              </div>
            );
          })
        )}
      </div>

      {/* Floating Jump-to-Bottom Button when user scrolls up */}
      {!autoScroll && logs.length > 0 && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-3 right-4 px-3 py-1.5 rounded-full bg-blue-600 hover:bg-blue-700 text-white text-[11px] font-sans font-bold flex items-center gap-1.5 shadow-md transition animate-bounce cursor-pointer z-10"
        >
          <ArrowDown className="w-3.5 h-3.5" />
          <span>Jump to Latest Logs</span>
        </button>
      )}
    </div>
  );
}
