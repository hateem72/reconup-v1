import React, { useState } from 'react';
import { AlertOctagon, CheckCircle2, XCircle, Sparkles, ShieldAlert, Cpu } from 'lucide-react';

export default function ExceptionQueue({ exceptions, batchId, onExceptionResolved }) {
  const [processingId, setProcessingId] = useState(null);

  if (!exceptions || exceptions.length === 0) {
    return (
      <div className="glass-panel p-6 mb-8 border border-emerald-500/25 bg-gradient-to-r from-emerald-500/10 via-emerald-500/5 to-transparent text-center">
        <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-white">Zero Unresolved Exceptions</h3>
        <p className="text-xs text-gray-400 max-w-lg mx-auto mt-1">
          All records in this batch resolved with 100% precision through the deterministic engine & persistent rule registry.
        </p>
      </div>
    );
  }

  const pendingExceptions = exceptions.filter(e => e.status === 'PENDING');

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
    <div className="glass-panel p-6 mb-8 border border-amber-500/30 bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-5 border-b border-amber-500/20 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/20 border border-amber-500/30 text-amber-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-white flex items-center gap-2">
              Human Governance Queue: Unknown Financial Patterns
            </h2>
            <p className="text-xs text-amber-200/80">AI agent isolated new marketplace deduction rules requiring verification</p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-sm">
          {pendingExceptions.length} Rule Approval Needed
        </span>
      </div>

      <div className="space-y-4">
        {pendingExceptions.map((exc) => {
          const confidencePct = Math.round(exc.confidence * 100);
          return (
            <div key={exc.id} className="p-5 rounded-2xl bg-gray-900/90 border border-gray-800 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-5 shadow-lg hover:border-gray-700 transition">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs font-mono font-extrabold text-amber-400 bg-amber-400/10 px-2.5 py-1 rounded-lg border border-amber-400/20">
                    Pattern: {exc.raw_status || exc.exception_type}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs text-gray-400">
                    <Cpu className="w-3.5 h-3.5 text-blue-400" />
                    <span>Agent Confidence:</span>
                    <span className="font-mono font-bold text-gray-200">{confidencePct}%</span>
                  </div>
                </div>

                <p className="text-xs text-gray-200 font-medium leading-relaxed mb-3">{exc.description}</p>

                {/* AI Rule Recommendation Card */}
                <div className="p-3 rounded-xl bg-gray-950 border border-gray-800/80 flex items-start gap-2 text-xs">
                  <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-indigo-300">AI Recommendation:</span>
                    <span className="text-gray-300 ml-1">
                      Classify pattern <strong>'{exc.raw_status}'</strong> as <span className="text-rose-400 font-semibold">SUBTRACT DEDUCTION</span>. Approving will persist this rule to SQLite database and reprocess all affected records.
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3 w-full lg:w-auto justify-end border-t lg:border-t-0 border-gray-800 pt-3 lg:pt-0">
                <button
                  onClick={() => handleReject(exc.id)}
                  disabled={processingId === exc.id}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4 inline mr-1.5" />
                  Reject
                </button>
                <button
                  onClick={() => handleApprove(exc.id, exc.raw_status)}
                  disabled={processingId === exc.id}
                  className="px-5 py-2 rounded-xl text-xs font-extrabold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg glow-emerald transition disabled:opacity-50"
                >
                  <CheckCircle2 className="w-4 h-4 inline mr-1.5" />
                  Approve Rule & Reprocess Batch
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
