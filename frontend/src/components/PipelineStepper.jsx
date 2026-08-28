import React from 'react';
import { Upload, Filter, Grid, CheckCircle2, AlertTriangle, DollarSign, MessageSquare, Tag, Loader2, Play } from 'lucide-react';

export default function PipelineStepper({ 
  currentStep, 
  setStep, 
  pendingExceptionsCount = 0,
  nodeStates = {},
  activeNodeMessage = ''
}) {
  const steps = [
    { id: 1, name: '1. Ingest & Profile', icon: Upload, desc: 'Exact Header Inspection' },
    { id: 2, name: '2. Sub-Tab Filter', icon: Filter, desc: 'Human Sheet Toggles' },
    { id: 3, name: '3. LLM Mapping', icon: Grid, desc: 'Human Column Selectors' },
    { id: 4, name: '4. Status Normalization', icon: Tag, desc: 'Human Status Selectors' },
    { id: 5, name: '5. Order Reconciliation', icon: DollarSign, desc: '3-Way Net Payouts' },
    { id: 6, name: '6. AI Exceptions & Q&A', icon: MessageSquare, desc: 'Governance Queue & Chat' },
  ];

  return (
    <div className="mb-8 rounded-2xl bg-white border border-slate-200 p-3 shadow-xs">
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
        {steps.map((step) => {
          const Icon = step.icon;
          const isSelected = currentStep === step.id;
          const state = nodeStates[step.id] || (currentStep > step.id ? 'completed' : isSelected ? 'running' : 'pending');
          const isRunning = state === 'running';
          const isCompleted = state === 'completed';

          return (
            <button
              key={step.id}
              onClick={() => setStep(step.id)}
              className={`p-3 rounded-xl text-left transition-all duration-200 flex flex-col justify-between border relative overflow-hidden cursor-pointer ${
                isRunning
                  ? 'bg-blue-50/90 border-blue-500 text-blue-900 shadow-md ring-2 ring-blue-500/20'
                  : isSelected
                  ? 'bg-indigo-50/80 border-indigo-500 text-indigo-950 shadow-xs'
                  : isCompleted
                  ? 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100/80'
                  : 'bg-slate-50/40 border-slate-200 text-slate-400 hover:text-slate-600'
              }`}
            >
              {/* Top Animated Progress Bar for Running Step */}
              {isRunning && (
                <div className="absolute top-0 right-0 left-0 h-1 bg-gradient-to-r from-blue-500 via-cyan-400 to-blue-600 animate-pulse" />
              )}
              
              <div className="flex items-center justify-between mb-1.5">
                <div
                  className={`p-1.5 rounded-lg transition-colors ${
                    isRunning
                      ? 'bg-blue-600 text-white shadow-xs'
                      : isSelected
                      ? 'bg-indigo-600 text-white'
                      : isCompleted
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {/* State Badges */}
                {isRunning ? (
                  <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-blue-100 text-blue-800 border border-blue-300 flex items-center gap-1 animate-pulse">
                    <Loader2 className="w-2.5 h-2.5 animate-spin" />
                    LIVE
                  </span>
                ) : isCompleted ? (
                  <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center gap-1">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    DONE
                  </span>
                ) : step.id === 6 && pendingExceptionsCount > 0 ? (
                  <span className="px-1.5 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-100 text-amber-800 border border-amber-300 flex items-center gap-1">
                    <AlertTriangle className="w-2.5 h-2.5" />
                    {pendingExceptionsCount}
                  </span>
                ) : null}
              </div>

              <div>
                <span className="text-xs font-extrabold block truncate">{step.name}</span>
                <span className="text-[10px] text-slate-500 font-medium block truncate">
                  {isRunning && activeNodeMessage ? activeNodeMessage : step.desc}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
