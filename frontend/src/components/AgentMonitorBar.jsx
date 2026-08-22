import React from 'react';
import { Bot, CheckCircle2, Clock, Activity, ShieldCheck } from 'lucide-react';

export default function AgentMonitorBar({ activeStep, retainedSheetsCount, droppedSheetsCount }) {
  const agents = [
    {
      id: 1,
      name: 'SheetRelevanceAgent',
      role: 'Sub-Tab Relevance Classifier',
      model: 'qwen2.5:3b',
      activeStep: 2,
      description: `Evaluates workbook sub-tabs & drops non-essential summary/disclaimer tabs`,
      badge: retainedSheetsCount ? `${retainedSheetsCount} Retained / ${droppedSheetsCount || 0} Dropped` : 'Ready'
    },
    {
      id: 2,
      name: 'ColumnMappingAgent',
      role: 'LLM Schema Mapper',
      model: 'qwen2.5:3b',
      activeStep: 3,
      description: `Maps raw spreadsheet column headers to canonical order_id, amount, status & sku`,
      badge: 'Smart Schema Cache'
    },
    {
      id: 3,
      name: 'StatusNormalizationAgent',
      role: 'Lifecycle State Classifier',
      model: 'qwen2.5:3b',
      activeStep: 3,
      description: `Categorizes raw status strings into Delivered, Return, RTO, Cancelled & Claim`,
      badge: '100% Status Coverage'
    },
    {
      id: 4,
      name: 'ReconciliationEngine',
      role: 'Deterministic Payout Matcher',
      model: 'Deterministic',
      activeStep: 4,
      description: `Matches Order IDs, aggregates multi-event payouts & calculates Net Settlement Payout`,
      badge: '3-Way Reconciliation'
    },
    {
      id: 5,
      name: 'ExceptionInvestigationAgent',
      role: 'Financial Governance Agent',
      model: 'qwen2.5:3b',
      activeStep: 5,
      description: `Surfaces financial anomalies, missing costs & fee deductions for human approval`,
      badge: 'Human-in-the-Loop'
    }
  ];

  return (
    <div className="mb-8 rounded-2xl bg-white border border-slate-200 p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-blue-50 text-blue-700 border border-blue-200">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
              Autonomous AI Agent Fleet Monitor
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-blue-50 text-blue-700 border border-blue-200">
                5 Active Agents
              </span>
            </h3>
            <p className="text-xs text-slate-500 font-medium">Live agent reasoning state & execution pipeline</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {agents.map((agent) => {
          const isActive = activeStep >= agent.activeStep;
          return (
            <div
              key={agent.id}
              className={`p-3.5 rounded-xl border transition-all duration-300 ${
                isActive
                  ? 'bg-blue-50/50 border-blue-200 shadow-xs'
                  : 'bg-slate-50 border-slate-200 opacity-70'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono font-bold text-slate-800 truncate max-w-[120px]">
                  {agent.name}
                </span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                    isActive
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      : 'bg-slate-200 text-slate-600'
                  }`}
                >
                  {isActive ? 'RUNNING' : 'IDLE'}
                </span>
              </div>

              <p className="text-[10px] text-slate-600 font-medium leading-tight mb-2 line-clamp-2">
                {agent.description}
              </p>

              <div className="pt-2 border-t border-slate-200 flex items-center justify-between text-[9px] font-mono">
                <span className="text-blue-700 font-bold">{agent.model}</span>
                <span className="text-slate-500">{agent.badge}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
