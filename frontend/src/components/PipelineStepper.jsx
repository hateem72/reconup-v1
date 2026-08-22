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
    <div className="mb-8 rounded-2xl bg-white border border-slate-200 p-3 shadow-xs">
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
                  ? 'bg-blue-50 border-blue-600 text-blue-900 shadow-sm'
                  : isCompleted
                  ? 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                  : 'bg-slate-50/50 border-slate-200 text-slate-400 hover:text-slate-600'
              }`}
            >
              {isActive && (
                <div className="absolute top-0 right-0 left-0 h-1 bg-blue-600 animate-pulse" />
              )}
              
              <div className="flex items-center justify-between mb-1.5">
                <div
                  className={`p-1.5 rounded-lg ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : isCompleted
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {step.id === 5 && pendingExceptionsCount > 0 && (
                  <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1">
                    <AlertTriangle className="w-2.5 h-2.5" />
                    {pendingExceptionsCount}
                  </span>
                )}
              </div>

              <div>
                <span className="text-xs font-extrabold block truncate">{step.name}</span>
                <span className="text-[10px] text-slate-500 font-medium block truncate">{step.desc}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
