import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Maximize2, Minimize2, Trash2, ChevronRight, Zap, RefreshCw, ArrowDown } from 'lucide-react';

export default function TerminalConsole({ batchId, isProcessing, liveLogs = [] }) {
  const [logs, setLogs] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isLiveStreamActive, setIsLiveStreamActive] = useState(false);
  const terminalContainerRef = useRef(null);

  // Sync external liveLogs if provided by parent App.jsx SSE listener
  useEffect(() => {
    if (liveLogs && liveLogs.length > 0) {
      setLogs(liveLogs);
      setIsLiveStreamActive(true);
    }
  }, [liveLogs]);

  // Establish SSE EventSource or Polling fallback
  useEffect(() => {
    if (!batchId) {
      setLogs([]);
      setIsLiveStreamActive(false);
      return;
    }

    let eventSource = null;

    try {
      eventSource = new EventSource(`/api/batches/${batchId}/stream`);
      
      eventSource.addEventListener('LOG', (event) => {
        try {
          const logItem = JSON.parse(event.data);
          const line = `[${logItem.stage || 'STAGE'}] ${logItem.message}`;
          setLogs((prev) => [...prev, line]);
          setIsLiveStreamActive(true);
        } catch (e) {
          console.error("Error parsing SSE log:", e);
        }
      });

      eventSource.addEventListener('CONNECTED', () => {
        setIsLiveStreamActive(true);
      });

      eventSource.onerror = () => {
        setIsLiveStreamActive(false);
      };
    } catch (e) {
      console.warn("SSE stream initialization fallback to polling:", e);
    }

    // Polling fallback to ensure initial or historical logs load
    const fetchLogs = async () => {
      try {
        const res = await fetch(`/api/batches/${batchId}/logs`);
        if (res.ok) {
          const data = await res.json();
          if (data.logs && data.logs.length > 0) {
            const formatted = data.logs.map(
              (l) => `[${l.stage || 'STAGE'}] ${l.description}`
            );
            setLogs((prev) => (prev.length === 0 ? formatted : prev));
          }
        }
      } catch (err) {
        console.error("Error fetching audit logs:", err);
      }
    };

    fetchLogs();

    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [batchId]);

  // Handle user scroll detection
  const handleScroll = () => {
    if (terminalContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = terminalContainerRef.current;
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
          {isLiveStreamActive || isProcessing ? (
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-300 font-bold flex items-center gap-1 animate-pulse">
              <Zap className="w-3 h-3 text-emerald-600 fill-emerald-600" />
              ⚡ Live SSE Stream
            </span>
          ) : (
            <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-200 text-slate-700 border border-slate-300 font-bold">
              ✓ Synced
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setLogs([])}
            className="p-1 text-slate-500 hover:text-slate-800 transition cursor-pointer"
            title="Clear Terminal Logs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-slate-500 hover:text-slate-800 transition cursor-pointer"
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
          <div className="text-slate-500 flex items-center gap-2 italic">
            <ChevronRight className="w-3 h-3 text-slate-600 animate-pulse" />
            Waiting for ingest pipeline execution or batch selection...
          </div>
        ) : (
          logs.map((log, index) => {
            let color = 'text-slate-300';
            if (log.includes('[INGEST]') || log.includes('[NODE 1]')) color = 'text-cyan-400';
            if (log.includes('[NODE 1.5]') || log.includes('[RELEVANCE]')) color = 'text-purple-400';
            if (log.includes('[NODE 2]') || log.includes('[VALIDATOR]')) color = 'text-yellow-400';
            if (log.includes('[NODE 3]') || log.includes('[NORMALIZER]')) color = 'text-blue-400';
            if (log.includes('[NODE 4]') || log.includes('[PATTERN]')) color = 'text-orange-400';
            if (log.includes('[NODE 5]') || log.includes('[RECONCILER]')) color = 'text-emerald-400';
            if (log.includes('[AGENT]')) color = 'text-indigo-300 font-semibold';
            if (log.includes('[ERROR]')) color = 'text-rose-400 font-bold';

            return (
              <div key={index} className="flex items-start gap-2 leading-relaxed hover:bg-slate-900/50 rounded px-1 -mx-1">
                <span className="text-slate-600 select-none">{String(index + 1).padStart(3, '0')}</span>
                <span className={color}>{log}</span>
              </div>
            );
          })
        )}
      </div>

      {!autoScroll && logs.length > 0 && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-3 right-4 px-2.5 py-1 rounded-full bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold shadow-lg flex items-center gap-1.5 transition cursor-pointer"
        >
          <ArrowDown className="w-3 h-3" />
          <span>Scroll to latest</span>
        </button>
      )}
    </div>
  );
}
