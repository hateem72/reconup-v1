import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, ShieldAlert, Bot, DollarSign, ArrowRight } from 'lucide-react';

export default function ExceptionsView({ exceptions, batchId, onExceptionResolved, onNext }) {
  const [approvingId, setApprovingId] = useState(null);

  const handleApproveRule = async (rulePattern) => {
    setApprovingId(rulePattern);
    try {
      const res = await fetch('/api/rules/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_id: f`rule-${rulePattern}`,
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
    <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-white">Step 5: Human-in-the-Loop Financial Governance</h2>
            <p className="text-xs text-slate-400">
              Autonomous Agent <strong className="text-amber-300">ExceptionInvestigationAgent</strong> surfaced unresolved items for human approval
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
          Governance Queue
        </span>
      </div>

      <div className="space-y-4">
        {!exceptions || exceptions.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-950 text-center text-slate-400 text-xs">
            ✓ 0 Unresolved Exception Items. All financial rules & status classifications are fully verified!
          </div>
        ) : (
          exceptions.map((exc, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    {exc.exception_type || 'FINANCIAL ANOMALY'}
                  </span>
                  <span className="text-xs font-bold text-white">
                    {exc.pattern || exc.description || 'Unidentified Fee Deduction Pattern'}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  {exc.llm_explanation || exc.rationale || 'Surfaced line items require human confirmation before P&L finalization.'}
                </p>
              </div>

              <button
                onClick={() => handleApproveRule(exc.pattern || 'Return Assurance Fee')}
                disabled={approvingId === exc.pattern}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 flex items-center gap-1.5 transition shrink-0"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Approve & Apply Standard Rule</span>
              </button>
            </div>
          ))
        )}
      </div>

      <div className="flex justify-end pt-4 border-t border-slate-800">
        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-2 transition"
        >
          <span>Proceed to Step 6: AI Finance Controller Q&A Console</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
