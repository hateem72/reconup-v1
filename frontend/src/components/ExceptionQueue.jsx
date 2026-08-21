import React, { useState } from 'react';
import { AlertOctagon, CheckCircle2, XCircle, Sparkles, ArrowRight } from 'lucide-react';

export default function ExceptionQueue({ exceptions, batchId, onExceptionResolved }) {
  const [processingId, setProcessingId] = useState(null);

  if (!exceptions || exceptions.length === 0) {
    return (
      <div className="glass-panel p-6 mb-8 border border-emerald-500/20 bg-emerald-500/5 text-center">
        <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-white">Zero Unresolved Exceptions</h3>
        <p className="text-xs text-gray-400">All transactions in this batch resolved with high confidence by deterministic engine & learned rule registry.</p>
      </div>
    );
  }

  const handleApprove = async (id, rawStatus) => {
    setProcessingId(id);
    try {
      const res = await fetch(`/api/exceptions/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision: 'APPROVE',
          note: 'Approved by finance operator',
          target_category: rawStatus.toUpperCase(),
          financial_effect: 'SUBTRACT'
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Approval failed');
      onExceptionResolved(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (id) => {
    setProcessingId(id);
    try {
      const res = await fetch(`/api/exceptions/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: 'REJECT', note: 'Rejected by human operator' })
      });
      const data = await res.json();
      onExceptionResolved(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="glass-panel p-6 mb-8 border border-amber-500/30 bg-amber-500/5">
      <div className="flex items-center justify-between mb-4 border-b border-amber-500/20 pb-3">
        <div className="flex items-center gap-2">
          <AlertOctagon className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-semibold text-white">Human Governance Queue: Unknown Financial Patterns</h2>
        </div>
        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          {exceptions.filter(e => e.status === 'PENDING').length} Action Required
        </span>
      </div>

      <div className="space-y-4">
        {exceptions.map((exc) => (
          <div key={exc.id} className="p-4 rounded-xl bg-gray-900 border border-gray-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                  {exc.raw_status || exc.exception_type}
                </span>
                <span className="text-xs text-gray-400">Confidence: {(exc.confidence * 100).toFixed(0)}%</span>
              </div>
              <p className="text-xs text-gray-200 font-medium">{exc.description}</p>
              <div className="mt-2 flex items-center gap-2 text-[11px] text-gray-400 bg-gray-950 p-2 rounded-lg border border-gray-800">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                <span>AI Suggestion: Classify as <strong>SUBTRACT DEDUCTION</strong> & persist rule for future batches.</span>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => handleReject(exc.id)}
                disabled={processingId === exc.id || exc.status !== 'PENDING'}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition disabled:opacity-50"
              >
                <XCircle className="w-3.5 h-3.5 inline mr-1" />
                Reject
              </button>
              <button
                onClick={() => handleApprove(exc.id, exc.raw_status)}
                disabled={processingId === exc.id || exc.status !== 'PENDING'}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition disabled:opacity-50"
              >
                <CheckCircle2 className="w-3.5 h-3.5 inline mr-1" />
                Approve Rule & Reprocess
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
