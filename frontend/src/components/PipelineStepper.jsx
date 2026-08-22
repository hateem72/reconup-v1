import React from 'react';
import { Upload, FileSearch, ShieldAlert, FileText, MessageSquare, CheckCircle2, ChevronRight } from 'lucide-react';

export default function PipelineStepper({ currentStep, setStep, pendingExceptionsCount, missingCostCount }) {
  const steps = [
    {
      id: 1,
      title: "1. Upload Data",
      subtitle: "Order & Payment Files",
      icon: Upload,
      badge: null
    },
    {
      id: 2,
      title: "2. Profile & Mapping",
      subtitle: "Column Validation",
      icon: FileSearch,
      badge: null
    },
    {
      id: 3,
      title: "3. Reconciliation Governance",
      subtitle: "Reconcile & Exceptions",
      icon: ShieldAlert,
      badge: pendingExceptionsCount > 0 ? `${pendingExceptionsCount} Discrepancies` : null,
      badgeColor: "bg-amber-100 text-amber-800 border-amber-300"
    },
    {
      id: 4,
      title: "4. P&L Analysis",
      subtitle: "SKU Profit & Margins",
      icon: FileText,
      badge: missingCostCount > 0 ? `${missingCostCount} Cost Missing` : null,
      badgeColor: "bg-amber-100 text-amber-800 border-amber-300"
    },
    {
      id: 5,
      title: "5. AI Q&A Console",
      subtitle: "Fact-backed Q&A",
      icon: MessageSquare,
      badge: null
    }
  ];

  return (
    <div className="glass-panel p-3 mb-8 shadow-soft bg-white border border-slate-200">
      <div className="flex flex-col md:flex-row items-stretch justify-between gap-2">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isActive = currentStep === step.id;
          const isCompleted = currentStep > step.id;

          return (
            <React.Fragment key={step.id}>
              <button
                onClick={() => setStep(step.id)}
                className={`flex-1 flex items-center gap-3 p-3 rounded-xl transition text-left relative ${
                  isActive
                    ? 'bg-blue-50 border-2 border-blue-600 text-blue-900 shadow-sm'
                    : isCompleted
                    ? 'bg-slate-50 border border-slate-200 text-slate-700 hover:bg-slate-100'
                    : 'bg-white border border-slate-200 text-slate-500 hover:bg-slate-50'
                }`}
              >
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md'
                      : isCompleted
                      ? 'bg-emerald-500 text-white'
                      : 'bg-slate-100 text-slate-600 border border-slate-200'
                  }`}
                >
                  {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : <Icon className="w-4 h-4" />}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className={`text-xs font-extrabold truncate ${isActive ? 'text-blue-900' : 'text-slate-800'}`}>
                      {step.title}
                    </span>
                    {step.badge && (
                      <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${step.badgeColor}`}>
                        {step.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-500 truncate mt-0.5">{step.subtitle}</p>
                </div>

                {idx < steps.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-slate-300 hidden md:block shrink-0" />
                )}
              </button>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
