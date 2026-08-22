import React from 'react';
import { Upload, Filter, Grid, CheckCircle2, AlertTriangle, DollarSign, MessageSquare } from 'lucide-react';

export default function PipelineStepper({ currentStep, setStep, pendingExceptionsCount }) {
  const steps = [
    { id: 1, name: '1. Ingest Data', icon: Upload, desc: 'Upload Orders & Payments' },
    { id: 2, name: '2. AI Sub-Tab Filter', icon: Filter, desc: 'SheetRelevanceAgent' },
    { id: 3, name: '3. LLM Mapping Matrix', icon: Grid, desc: 'ColumnMappingAgent' },
    { id: 4, name: '4. Order Reconciliation', icon: CheckCircle2, desc: 'ReconciliationEngine' },
    { id: 5, name: '5. AI Exceptions & P&L', icon: DollarSign, desc: 'Human Governance' },
    { id: 6, name: '6. AI Q&A Console', icon: MessageSquare, desc: 'Natural Language Agent' },
  ];

  return (
    <div className="mb-8 rounded-2xl bg-slate-900 border border-slate-800 p-3 shadow-xl">
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
        {steps.map((step) => {
          const Icon = step.icon;
          const isActive = currentStep === step.id;
          const isCompleted = currentStep > step.id;

          return (
            <button
              key={step.id}
              onClick={() => setStep(step.id)}
              className={`p-3 rounded-xl text-left transition-all duration-200 flex flex-col justify-between border relative overflow-hidden ${
                isActive
                  ? 'bg-gradient-to-tr from-blue-900/60 to-indigo-950/80 border-blue-500 text-white shadow-lg shadow-blue-500/10'
                  : isCompleted
                  ? 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
                  : 'bg-slate-950/20 border-slate-900 text-slate-500 hover:text-slate-400'
              }`}
            >
              {isActive && (
                <div className="absolute top-0 right-0 left-0 h-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 animate-pulse" />
              )}
              
              <div className="flex items-center justify-between mb-1.5">
                <div
                  className={`p-1.5 rounded-lg ${
                    isActive
                      ? 'bg-blue-500/20 text-cyan-400 border border-blue-500/30'
                      : isCompleted
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : 'bg-slate-800/50 text-slate-600'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {step.id === 5 && pendingExceptionsCount > 0 && (
                  <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                    <AlertTriangle className="w-2.5 h-2.5" />
                    {pendingExceptionsCount}
                  </span>
                )}
              </div>

              <div>
                <span className="text-xs font-bold block truncate">{step.name}</span>
                <span className="text-[10px] text-slate-400 block truncate">{step.desc}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
