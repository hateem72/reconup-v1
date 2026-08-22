import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles } from 'lucide-react';

export default function FinanceQAChat({ batchId }) {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! I am your AI Finance Operations Analyst. You can ask me questions about specific order payouts, match statuses, P&L SKU margins, or financial rules.'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userText = query.trim();
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setQuery('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userText,
          batch_id: batchId
        })
      });
      const data = await res.json();
      if (res.ok) {
        setMessages(prev => [...prev, { sender: 'agent', text: data.response }]);
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
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-3 border-b border-slate-200 pb-4">
        <div className="p-3 rounded-2xl bg-cyan-50 text-cyan-600 border border-cyan-200">
          <MessageSquare className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-base font-extrabold text-slate-900">Step 6: AI Finance Controller Interactive Q&A</h2>
          <p className="text-xs text-slate-500 font-medium">
            Ask any question regarding specific Order IDs, payout aggregations, or financial exceptions
          </p>
        </div>
      </div>

      <div className="h-80 overflow-y-auto space-y-3 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.sender === 'agent' && (
              <div className="p-1.5 rounded-lg bg-cyan-100 text-cyan-800 border border-cyan-200 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
            )}
            <div
              className={`p-3 rounded-xl max-w-lg leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-blue-600 text-white font-medium shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-800 font-mono shadow-xs'
              }`}
            >
              {m.text}
            </div>
            {m.sender === 'user' && (
              <div className="p-1.5 rounded-lg bg-blue-100 text-blue-800 shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-bold">
            <Sparkles className="w-4 h-4 animate-spin text-cyan-600" />
            <span>AI Agent querying database tools...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          placeholder="Ask a question (e.g., 'What is the payout for ORD-1001?')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-mono"
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5 transition disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          <span>Ask Agent</span>
        </button>
      </form>
    </div>
  );
}
