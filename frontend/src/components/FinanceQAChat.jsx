import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles } from 'lucide-react';

export default function FinanceQAChat({ batchId }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am your AI Finance Controller. Ask me questions about order statuses, profit breakdowns, or unresolved exceptions.'
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
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
    "What is my reconciliation match rate?",
    "Which SKU produced the highest profit?",
    "Why are some records unresolved?"
  ];

  return (
    <div className="glass-panel p-6 mb-8 border border-gray-800">
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-800">
        <MessageSquare className="w-5 h-5 text-purple-400" />
        <h2 className="text-base font-semibold text-white">Finance Operations Q&A Assistant</h2>
      </div>

      {/* Messages Window */}
      <div className="space-y-3 mb-4 max-h-64 overflow-y-auto pr-2">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.sender === 'bot' && (
              <div className="w-7 h-7 rounded-lg bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
            )}
            <div className={`p-3 rounded-xl text-xs max-w-md ${m.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-900 border border-gray-800 text-gray-200'}`}>
              {m.text}
            </div>
            {m.sender === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-xs text-gray-400 italic">
            <Sparkles className="w-4 h-4 text-purple-400 animate-spin" />
            Querying structured database records...
          </div>
        )}
      </div>

      {/* Sample Question Chips */}
      <div className="flex flex-wrap gap-2 mb-3">
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => setQuestion(q)}
            className="text-[11px] px-2.5 py-1 rounded-lg bg-gray-900 hover:bg-gray-800 border border-gray-800 text-gray-300 transition"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Form Input */}
      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about specific orders or batch financial summary..."
          className="flex-1 px-3 py-2 rounded-xl bg-gray-900 border border-gray-800 text-xs text-gray-200 focus:outline-none focus:border-purple-500"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1 disabled:opacity-50"
        >
          <Send className="w-3.5 h-3.5" />
          Ask
        </button>
      </form>
    </div>
  );
}
