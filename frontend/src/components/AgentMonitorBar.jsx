import React from 'react';
import { Bot, CheckCircle2, Clock, Activity, ShieldCheck, Database, Layers } from 'lucide-react';

export default function AgentMonitorBar({ activeStep, retainedSheetsCount, droppedSheetsCount }) {
  const agents = [
    {
      id: 1,
      name: 'SheetRelevanceAgent',
      role: 'Sub-Tab Relevance AI Classifier',
      model: 'qwen2.5:3b',
      activeStep: 2,
      description: `Evaluates workbook sub-tabs & drops non-essential summary/disclaimer tabs`,
      status: activeStep >= 2 ? 'ACTIVE' : 'READY',
      badge: retainedSheetsCount ? `${retainedSheetsCount} Retained / ${droppedSheetsCount || 0} Dropped` : 'Ready'
    },
    {
      id: 2,
      name: 'ColumnMappingAgent',
      role: 'LLM Semantic Schema Mapper',
      model: 'qwen2.5:3b',
      activeStep: 3,
      description: `Maps raw spreadsheet column headers to canonical order_id, amount, status & sku`,
      status: activeStep >= 3 ? 'ACTIVE' : 'WAITING',
      badge: 'Smart Schema Cache'
    },
    {
      id: 3,
      name: 'StatusNormalizationAgent',
      role: 'Order Lifecycle State Classifier',
      model: 'qwen2.5:3b',
      activeStep: 3,
      description: `Categorizes raw status strings into Delivered, Return, RTO, Cancelled & Claim`,
      status: activeStep >= 3 ? 'ACTIVE' : 'WAITING',
      badge: '100% Status Repair'
    },
    {
      id: 4,
      name: 'ReconciliationEngine',
      role: 'Deterministic Net Payout Matcher',
      model: 'Deterministic',
      activeStep: 4,
      description: `Matches Order IDs, aggregates multi-event payouts & calculates Net Settlement Payout`,
      status: activeStep >= 4 ? 'ACTIVE' : 'WAITING',
      badge: '3-Way Reconciliation'
    },
    {
      id: 5,
      name: 'ExceptionInvestigationAgent',
      role: 'Financial Governance & Rule Registry',
      model: 'qwen2.5:3b',
      activeStep: 5,
      description: `Surfaces financial anomalies, missing costs & fee deductions for human approval`,
      status: activeStep >= 5 ? 'ACTIVE' : 'WAITING',
      badge: 'Human-in-the-Loop'
    }
  ];

  return (
    <div className="mb-8 rounded-2xl bg-slate-900/90 border border-slate-800 p-5 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Autonomous AI Agent Intelligence Fleet
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-blue-500/20 text-blue-300 border border-blue-500/30">
                5 Active Agents
              </span>
            </h3>
            <p className="text-xs text-slate-400">Live agent reasoning state & model execution pipeline</p>
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
                  ? 'bg-slate-950/80 border-emerald-500/40 shadow-lg shadow-emerald-500/5'
                  : 'bg-slate-950/40 border-slate-800/60 opacity-70'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono font-bold text-slate-300 truncate max-w-[120px]">
                  {agent.name}
                </span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                    isActive
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  {isActive ? 'RUNNING' : 'IDLE'}
                </span>
              </div>

              <p className="text-[10px] text-slate-400 font-medium leading-tight mb-2 line-clamp-2">
                {agent.description}
              </p>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[9px] font-mono">
                <span className="text-cyan-400">{agent.model}</span>
                <span className="text-slate-400 font-bold">{agent.badge}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
