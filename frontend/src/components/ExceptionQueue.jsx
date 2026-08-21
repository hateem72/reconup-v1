import React, { useState } from 'react';
import { AlertOctagon, CheckCircle2, XCircle, Sparkles, ShieldAlert, Cpu } from 'lucide-react';

export default function ExceptionQueue({ exceptions, batchId, onExceptionResolved }) {
  const [processingId, setProcessingId] = useState(null);

  if (!exceptions || exceptions.length === 0) {
    return (
      <div className="glass-panel p-6 mb-8 border border-emerald-200 bg-emerald-50/50 text-center shadow-soft">
        <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
        <h3 className="text-sm font-extrabold text-slate-900">Zero Unresolved Exceptions</h3>
        <p className="text-xs text-slate-600 max-w-lg mx-auto mt-1 font-medium">
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
    <div className="glass-panel p-6 mb-8 border border-amber-200 bg-amber-50/40 shadow-soft">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-5 border-b border-amber-200 pb-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-100 border border-amber-300 text-amber-800">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              Step 3: Human Governance & Unknown Pattern Verification
            </h2>
            <p className="text-xs text-amber-900 font-medium">AI agent isolated new marketplace deduction rules requiring verification</p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-amber-200 text-amber-900 border border-amber-300 shadow-xs">
          {pendingExceptions.length} Rule Approvals Required
        </span>
      </div>

      <div className="space-y-4">
        {pendingExceptions.map((exc) => {
          const confidencePct = Math.round(exc.confidence * 100);
          return (
            <div key={exc.id} className="p-5 rounded-2xl bg-white border border-slate-200 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-5 shadow-sm hover:border-slate-300 transition">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs font-mono font-extrabold text-amber-800 bg-amber-100 px-2.5 py-1 rounded-lg border border-amber-200">
                    Pattern: {exc.raw_status || exc.exception_type}
                  </span>
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                    <Cpu className="w-3.5 h-3.5 text-blue-600" />
                    <span>Agent Confidence:</span>
                    <span className="font-mono font-bold text-slate-900">{confidencePct}%</span>
                  </div>
                </div>

                <p className="text-xs text-slate-800 font-semibold leading-relaxed mb-3">{exc.description}</p>

                {/* AI Rule Recommendation Box */}
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-start gap-2 text-xs">
                  <Sparkles className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-indigo-900">AI Recommendation:</span>
                    <span className="text-slate-700 ml-1 font-medium">
                      Classify pattern <strong>'{exc.raw_status}'</strong> as <span className="text-rose-600 font-extrabold">SUBTRACT DEDUCTION</span>. Approving will persist this rule to SQLite database and reprocess all affected records.
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-3 w-full lg:w-auto justify-end border-t lg:border-t-0 border-slate-200 pt-3 lg:pt-0">
                <button
                  onClick={() => handleReject(exc.id)}
                  disabled={processingId === exc.id}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 transition disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4 inline mr-1.5" />
                  Reject
                </button>
                <button
                  onClick={() => handleApprove(exc.id, exc.raw_status)}
                  disabled={processingId === exc.id}
                  className="px-5 py-2 rounded-xl text-xs font-extrabold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md transition disabled:opacity-50"
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
