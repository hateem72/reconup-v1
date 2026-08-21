import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, HelpCircle, Terminal } from 'lucide-react';

export default function FinanceQAChat({ batchId }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Finance Controller Assistant. I query structured database facts to answer questions without financial hallucinations.'
    }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!question.trim()) return;

    const userText = question.trim();
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch('/api/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userText, batch_id: batchId })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'bot', text: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: 'Error retrieving database facts.' }]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "What is my match rate?",
    "Which SKU is most profitable?",
    "Why are records unresolved?"
  ];

  return (
    <div className="glass-panel p-6 mb-8 border border-purple-500/20 bg-gradient-to-b from-purple-500/5 via-transparent to-transparent flex flex-col h-[520px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-gray-800 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-400">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-extrabold text-white">Finance Q&A Command Console</h2>
            <p className="text-[10px] text-gray-400">Deterministic Tool-backed Agent</p>
          </div>
        </div>
        <span className="flex items-center gap-1.5 text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-dot"></span>
          Connected
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto my-4 space-y-3 pr-2">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.sender === 'bot' && (
              <div className="w-7 h-7 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0 shadow-sm">
                <Bot className="w-4 h-4" />
              </div>
            )}
            <div
              className={`p-3.5 rounded-2xl text-xs leading-relaxed max-w-[85%] ${
                m.sender === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-md'
                  : 'bg-gray-900/90 border border-gray-800 text-gray-200 rounded-bl-none shadow-sm font-sans'
              }`}
            >
              {m.text}
            </div>
            {m.sender === 'user' && (
              <div className="w-7 h-7 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0 shadow-sm">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-purple-400 italic bg-purple-500/10 p-2.5 rounded-xl border border-purple-500/20 w-fit">
            <Sparkles className="w-4 h-4 text-purple-400 animate-spin" />
            Querying SQLite database records...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Question Chips */}
      <div className="flex flex-wrap gap-1.5 mb-3 shrink-0">
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => { setQuestion(q); }}
            className="text-[10px] font-medium px-2.5 py-1 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 transition flex items-center gap-1 hover:border-gray-700"
          >
            <HelpCircle className="w-3 h-3 text-purple-400" />
            {q}
          </button>
        ))}
      </div>

      {/* Form Input */}
      <form onSubmit={handleSend} className="flex gap-2 shrink-0">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about specific orders or settlement summaries..."
          className="flex-1 px-3.5 py-2.5 rounded-xl bg-gray-900 border border-gray-800 text-xs text-gray-200 focus:outline-none focus:border-purple-500 font-sans"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-4 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-extrabold flex items-center gap-1.5 shadow-md disabled:opacity-50 transition"
        >
          <Send className="w-3.5 h-3.5" />
          Ask
        </button>
      </form>
    </div>
  );
}
