import React from 'react';
import { CheckCircle2, AlertTriangle, Zap, TrendingUp } from 'lucide-react';

export default function MetricsCards({ metrics, summary }) {
  if (!metrics) return null;

  const cards = [
    {
      title: "Reconciliation Match Rate",
      value: `${metrics.match_rate}%`,
      subtitle: `${metrics.records_matched} / ${metrics.total_records} records matched`,
      progressPct: metrics.match_rate,
      icon: CheckCircle2,
      color: "text-emerald-600",
      bg: "bg-emerald-50/60 border-emerald-200",
      barColor: "bg-emerald-500"
    },
    {
      title: "Net Profit / Loss",
      value: `₹${(summary?.totalProfit ?? metrics.total_profit ?? 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`,
      subtitle: `Revenue: ₹${(summary?.totalDeliveredSales ?? metrics.total_revenue ?? 0).toLocaleString('en-IN')}`,
      progressPct: (metrics.total_profit > 0) ? 85 : 15,
      icon: TrendingUp,
      color: (metrics.total_profit >= 0) ? "text-emerald-600" : "text-rose-600",
      bg: (metrics.total_profit >= 0) ? "bg-emerald-50/60 border-emerald-200" : "bg-rose-50/60 border-rose-200",
      barColor: (metrics.total_profit >= 0) ? "bg-emerald-500" : "bg-rose-500"
    },
    {
      title: "Unresolved Exceptions",
      value: metrics.unresolved_exceptions,
      subtitle: `Exposure: ₹${metrics.unresolved_financial_exposure?.toLocaleString('en-IN') || 0}`,
      progressPct: Math.min(100, metrics.unresolved_exceptions * 15),
      icon: AlertTriangle,
      color: metrics.unresolved_exceptions > 0 ? "text-amber-600" : "text-slate-500",
      bg: metrics.unresolved_exceptions > 0 ? "bg-amber-50/60 border-amber-200" : "bg-white border-slate-200",
      barColor: metrics.unresolved_exceptions > 0 ? "bg-amber-500" : "bg-slate-400"
    },
    {
      title: "Engine Throughput",
      value: `${metrics.throughput_records_per_sec.toLocaleString()} rec/s`,
      subtitle: `Latency: ${metrics.processing_time_ms} ms`,
      progressPct: 95,
      icon: Zap,
      color: "text-blue-600",
      bg: "bg-blue-50/60 border-blue-200",
      barColor: "bg-blue-600"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className={`p-5 rounded-2xl border ${card.bg} shadow-soft backdrop-blur-sm transition-all duration-300 hover:shadow-md`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-500">{card.title}</span>
              <div className={`p-2 rounded-xl bg-white border border-slate-200 shadow-xs ${card.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-extrabold text-slate-900 tracking-tight">{card.value}</div>
            <div className="text-xs text-slate-600 mt-1 font-medium">{card.subtitle}</div>
            
            {/* Micro Progress Bar */}
            <div className="w-full h-1.5 bg-slate-200/80 rounded-full mt-3 overflow-hidden">
              <div
                style={{ width: `${card.progressPct}%` }}
                className={`h-full rounded-full ${card.barColor}`}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
