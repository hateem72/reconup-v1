import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, Code, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';
import RawJsonModal from './RawJsonModal';

// Helper function to render GFM Markdown text and Markdown Tables cleanly
function FormattedMessage({ text }) {
  if (!text) return null;

  const lines = text.split('\n');
  const blocks = [];
  let inTable = false;
  let tableRows = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Table row detector
    if (line.startsWith('|') && line.endsWith('|')) {
      inTable = true;
      if (!line.includes('---')) {
        const cells = line.split('|').slice(1, -1).map(c => c.trim());
        tableRows.push(cells);
      }
    } else {
      if (inTable && tableRows.length > 0) {
        blocks.push({ type: 'table', rows: [...tableRows] });
        tableRows = [];
        inTable = false;
      }
      if (line) {
        blocks.push({ type: 'text', content: line });
      }
    }
  }
  if (inTable && tableRows.length > 0) {
    blocks.push({ type: 'table', rows: [...tableRows] });
  }

  return (
    <div className="space-y-2 font-sans text-xs leading-relaxed">
      {blocks.map((b, idx) => {
        if (b.type === 'table') {
          const header = b.rows[0] || [];
          const body = b.rows.slice(1) || [];

          return (
            <div key={idx} className="my-2 overflow-x-auto rounded-xl border border-slate-200 shadow-xs">
              <table className="w-full text-left border-collapse text-[11px]">
                <thead>
                  <tr className="bg-slate-100 border-b border-slate-200 text-slate-700 font-extrabold">
                    {header.map((h, hIdx) => (
                      <th key={hIdx} className="px-3 py-2 border-r last:border-r-0 border-slate-200 uppercase tracking-wider">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {body.map((row, rIdx) => (
                    <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-white' : 'bg-slate-50/60'}>
                      {row.map((cell, cIdx) => (
                        <td key={cIdx} className="px-3 py-2 border-t border-r last:border-r-0 border-slate-200 text-slate-800 font-medium">
                          {cell.includes('₹') ? (
                            <span className="font-extrabold text-slate-900">{cell}</span>
                          ) : cell.toLowerCase().includes('delivered') || cell.toLowerCase().includes('exact') ? (
                            <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">{cell}</span>
                          ) : cell.toLowerCase().includes('return') || cell.toLowerCase().includes('shortfall') || cell.toLowerCase().includes('missing') ? (
                            <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px]">{cell}</span>
                          ) : (
                            cell
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        const isHeader = b.content.startsWith('#') || b.content.startsWith('**');
        const cleanContent = b.content.replace(/^#+\s*/, '').replace(/\*\*/g, '');

        if (isHeader) {
          return (
            <h4 key={idx} className="font-extrabold text-slate-900 text-xs mt-2 mb-1 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600 inline" />
              {cleanContent}
            </h4>
          );
        }

        return (
          <p key={idx} className="text-slate-700 font-medium">
            {b.content}
          </p>
        );
      })}
    </div>
  );
}

export default function FinanceQAChat({ batchId }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! I am your AI Finance Controller Co-Pilot. Ask me about return costs, specific Order IDs, payout shortfalls, or match rate summaries.',
      sql_query: '',
      facts: []
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeJsonModal, setActiveJsonModal] = useState(null);
  const [expandedDebugIdx, setExpandedDebugIdx] = useState(null);

  const samplePrompts = [
    "What are the total return costs?",
    "What is the match rate and total payout?",
    "Show orders with payment shortfalls"
  ];

  const handleSend = async (userQuery) => {
    const textToSend = userQuery || query;
    if (!textToSend.trim()) return;

    setMessages(prev => [...prev, { sender: 'user', text: textToSend }]);
    if (!userQuery) setQuery('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: textToSend,
          batch_id: batchId
        })
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [
          ...prev, 
          { 
            sender: 'agent', 
            text: data.response || data.answer,
            sql_query: data.sql_query,
            sql_executed_safely: data.sql_executed_safely,
            facts_count: data.retrieved_facts_count || (data.retrieved_facts ? data.retrieved_facts.length : 0),
            facts: data.retrieved_facts
          }
        ]);
      } else {
        setMessages(prev => [...prev, { sender: 'agent', text: data.detail || "I ran the query tools but could not retrieve facts for this request." }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'agent', text: "Error connecting to AI QA tool backend." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-indigo-50 text-indigo-600 border border-indigo-200">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              Node 6: Interactive Settlement Q&A Co-Pilot
              <span className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[10px] font-mono font-bold">
                Text-to-SQL & Timeout Protected
              </span>
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Ask natural language questions to query database records, order statuses, and return costs
            </p>
          </div>
        </div>
      </div>

      {/* Suggested Quick Prompt Pills */}
      <div className="flex flex-wrap gap-2 pt-1">
        {samplePrompts.map((sp, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(sp)}
            className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 text-[11px] font-bold transition-all border border-slate-200 cursor-pointer"
          >
            💡 {sp}
          </button>
        ))}
      </div>

      {/* Messages Stream Container */}
      <div className="h-80 overflow-y-auto space-y-3 p-4 rounded-xl bg-slate-50/80 border border-slate-200 text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'agent' && (
              <div className="p-1.5 rounded-lg bg-indigo-600 text-white shrink-0 shadow-xs">
                <Bot className="w-4 h-4" />
              </div>
            )}
            <div className="max-w-2xl space-y-1.5">
              <div
                className={`p-4 rounded-2xl ${
                  m.sender === 'user'
                    ? 'bg-blue-600 text-white font-bold shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-900 shadow-xs'
                }`}
              >
                <FormattedMessage text={m.text} />
              </div>

              {/* Backend Debug Trace Panel */}
              {m.sender === 'agent' && (m.sql_query || m.facts) && (
                <div className="rounded-xl border border-slate-200 bg-slate-100/70 p-2 text-[10px]">
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setExpandedDebugIdx(expandedDebugIdx === idx ? null : idx)}
                      className="font-mono font-bold text-indigo-700 hover:underline flex items-center gap-1 cursor-pointer"
                    >
                      <Code className="w-3 h-3 text-indigo-600" />
                      Backend Debug Trace ({m.facts_count || 0} DB Facts)
                      {expandedDebugIdx === idx ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </button>
                    {m.facts && (
                      <button
                        onClick={() => setActiveJsonModal({ sql_query: m.sql_query, facts: m.facts })}
                        className="text-slate-500 font-bold hover:text-slate-800 cursor-pointer"
                      >
                        Inspect Raw Data
                      </button>
                    )}
                  </div>

                  {expandedDebugIdx === idx && m.sql_query && (
                    <div className="mt-2 p-2 rounded-lg bg-slate-900 text-slate-100 font-mono text-[10px] overflow-x-auto space-y-1">
                      <div className="text-emerald-400 font-bold">// Generated Read-Only SQL Query</div>
                      <div>{m.sql_query}</div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {m.sender === 'user' && (
              <div className="p-1.5 rounded-lg bg-slate-200 text-slate-700 shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-indigo-700 text-xs font-mono font-bold p-2 bg-indigo-50 rounded-xl border border-indigo-100 animate-pulse">
            <Sparkles className="w-4 h-4 animate-spin text-indigo-600" />
            <span>AI Agent executing Text-to-SQL and database query...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
        <input
          type="text"
          placeholder="Ask any question (e.g., 'What are the total return costs?')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500 font-mono"
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="px-6 py-3 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-2 transition disabled:opacity-50 shadow-xs cursor-pointer"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>

      {/* Raw JSON Modal */}
      {activeJsonModal && (
        <RawJsonModal
          title="Q&A Backend Debug Payload & Executed SQL"
          data={activeJsonModal}
          onClose={() => setActiveJsonModal(null)}
        />
      )}
    </div>
  );
}
