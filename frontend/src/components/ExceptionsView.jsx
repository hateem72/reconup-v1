import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert, Bot, DollarSign, ArrowRight, Code } from 'lucide-react';
import RawJsonModal from './RawJsonModal';

export default function ExceptionsView({ exceptions, batchId, onExceptionResolved, onNext }) {
  const [approvingId, setApprovingId] = useState(null);
  const [showJsonModal, setShowJsonModal] = useState(false);

  const handleApproveRule = async (rulePattern) => {
    setApprovingId(rulePattern);
    try {
      const res = await fetch('/api/rules/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_id: `rule-${rulePattern}`,
          pattern: rulePattern,
          normalized_category: 'Return Assurance Fee Deduction',
          financial_effect: 'SUBTRACT',
          auto_apply: true
        })
      });
      if (res.ok && onExceptionResolved) {
        onExceptionResolved();
      }
    } catch (err) {
      console.error("Error approving rule:", err);
    } finally {
      setApprovingId(null);
    }
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <RawJsonModal
        title="Node 7 Human Governance & Exception Queue"
        data={{ batch_id: batchId, total_exceptions: exceptions.length, exceptions: exceptions }}
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-amber-50 text-amber-600 border border-amber-200">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 6: Human-in-the-Loop Financial Governance</h2>
            <p className="text-xs text-slate-500 font-medium">
              Autonomous Agent <strong className="text-amber-800">ExceptionInvestigationAgent</strong> surfaced unresolved items for human approval
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowJsonModal(true)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-mono font-bold flex items-center gap-1.5 transition shadow-xs cursor-pointer"
            title="View Raw Backend JSON Payload"
          >
            <Code className="w-3.5 h-3.5 text-cyan-400" />
            <span>Raw JSON Data</span>
          </button>

          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-100 text-amber-800 border border-amber-200">
            Governance Queue
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {!exceptions || exceptions.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-50 border border-slate-200 text-center text-slate-600 text-xs font-bold">
            ✓ 0 Unresolved Exception Items. All financial rules & status classifications are fully verified!
          </div>
        ) : (
          exceptions.map((exc, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-amber-50/50 border border-amber-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-200 text-amber-900 border border-amber-300">
                    {exc.exception_type || 'FINANCIAL ANOMALY'}
                  </span>
                  <span className="text-xs font-extrabold text-slate-900">
                    {exc.pattern || exc.description || 'Unidentified Fee Deduction Pattern'}
                  </span>
                </div>
                <p className="text-xs text-slate-600 font-medium">
                  {exc.llm_explanation || exc.rationale || 'Surfaced line items require human confirmation before P&L finalization.'}
                </p>
              </div>

              <button
                onClick={() => handleApproveRule(exc.pattern || 'Return Assurance Fee')}
                disabled={approvingId === exc.pattern}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-1.5 transition shrink-0 shadow-xs cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve & Apply Standard Rule</span>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
