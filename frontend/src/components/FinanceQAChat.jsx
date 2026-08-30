import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, Code, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import RawJsonModal from './RawJsonModal';

// Helper function to render GFM Markdown text and Markdown Tables cleanly
function FormattedMessage({ text }) {
  if (!text) return null;

  // Split content into blocks (paragraphs vs tables vs code blocks)
  const lines = text.split('\n');
  const blocks = [];
  let inTable = false;
  let tableRows = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Table row detector
    if (line.startsWith('|') && line.endsWith('|')) {
      inTable = true;
      // Filter out divider rows like |---|---|
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
                          ) : cell.toLowerCase().includes('shortfall') || cell.toLowerCase().includes('missing') || cell.toLowerCase().includes('pending') ? (
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

        // Header lines (### or **Header**)
        const isHeader = b.content.startsWith('#') || b.content.startsWith('**');
        const cleanContent = b.content.replace(/^#+\s*/, '').replace(/\*\*/g, '');

        if (isHeader) {
          return (
            <h4 key={idx} className="font-extrabold text-slate-900 text-xs mt-2 mb-1 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600 inline" />
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
      text: 'Hello! I am your AI Finance Controller Assistant. Ask me about specific Order IDs, payout shortfalls, match rates, or financial exception rules.',
      sql_query: ''
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeSqlModal, setActiveSqlModal] = useState(null);

  const samplePrompts = [
    "What is the match rate and total payout?",
    "Show orders with payment shortfalls",
    "What are the top 3 unresolved exceptions?"
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
                Text-to-SQL Active
              </span>
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Ask natural language questions to query database records, order statuses, and settlement payouts
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
            <div className="max-w-2xl space-y-1">
              <div
                className={`p-4 rounded-2xl ${
                  m.sender === 'user'
                    ? 'bg-blue-600 text-white font-bold shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-900 shadow-xs'
                }`}
              >
                <FormattedMessage text={m.text} />
              </div>

              {/* View Generated SQL Button */}
              {m.sql_query && (
                <div className="flex items-center gap-2 px-1">
                  <button
                    onClick={() => setActiveSqlModal(m.sql_query)}
                    className="text-[10px] font-mono font-bold text-slate-400 hover:text-indigo-600 flex items-center gap-1 cursor-pointer"
                  >
                    <Code className="w-3 h-3" />
                    Inspect Executed SQL Query
                  </button>
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
            <span>AI Agent generating Text-to-SQL and inspecting database facts...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
        <input
          type="text"
          placeholder="Ask any question (e.g., 'Show payout details for ORD-2026-000003')"
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

      {/* SQL Modal */}
      {activeSqlModal && (
        <RawJsonModal
          title="Executed Read-Only SQLite Query"
          data={{ executed_sql: activeSqlModal }}
          onClose={() => setActiveSqlModal(null)}
        />
      )}
    </div>
  );
}
