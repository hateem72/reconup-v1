import React from 'react';
import { DollarSign, CheckCircle2, AlertTriangle, Zap, TrendingUp, Layers, ShieldCheck } from 'lucide-react';

export default function MetricsCards({ metrics, summary }) {
  if (!metrics) return null;

  const cards = [
    {
      title: "Reconciliation Match Rate",
      value: `${metrics.match_rate}%`,
      subtitle: `${metrics.records_matched} / ${metrics.total_records} records matched`,
      progressPct: metrics.match_rate,
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent border-emerald-500/25 glow-emerald"
    },
    {
      title: "Net Profit / Loss",
      value: `₹${(summary?.totalProfit ?? metrics.total_profit ?? 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`,
      subtitle: `Revenue: ₹${(summary?.totalDeliveredSales ?? metrics.total_revenue ?? 0).toLocaleString('en-IN')}`,
      progressPct: (metrics.total_profit > 0) ? 80 : 20,
      icon: TrendingUp,
      color: (metrics.total_profit >= 0) ? "text-emerald-400" : "text-rose-400",
      bg: (metrics.total_profit >= 0)
        ? "bg-gradient-to-br from-emerald-500/10 via-emerald-500/5 to-transparent border-emerald-500/25 glow-emerald"
        : "bg-gradient-to-br from-rose-500/10 via-rose-500/5 to-transparent border-rose-500/25"
    },
    {
      title: "Unresolved Exceptions",
      value: metrics.unresolved_exceptions,
      subtitle: `Exposure: ₹${metrics.unresolved_financial_exposure?.toLocaleString('en-IN') || 0}`,
      progressPct: Math.min(100, metrics.unresolved_exceptions * 15),
      icon: AlertTriangle,
      color: metrics.unresolved_exceptions > 0 ? "text-amber-400" : "text-gray-400",
      bg: metrics.unresolved_exceptions > 0
        ? "bg-gradient-to-br from-amber-500/10 via-amber-500/5 to-transparent border-amber-500/25 glow-amber"
        : "bg-gray-900/60 border-gray-800"
    },
    {
      title: "Engine Throughput",
      value: `${metrics.throughput_records_per_sec.toLocaleString()} rec/s`,
      subtitle: `Latency: ${metrics.processing_time_ms} ms`,
      progressPct: 95,
      icon: Zap,
      color: "text-blue-400",
      bg: "bg-gradient-to-br from-blue-500/10 via-blue-500/5 to-transparent border-blue-500/25 glow-blue"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className={`p-5 rounded-2xl border ${card.bg} backdrop-blur-md transition-all duration-300 hover:scale-[1.02]`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-extrabold uppercase tracking-wider text-gray-400">{card.title}</span>
              <div className={`p-2 rounded-xl bg-gray-900/80 border border-gray-800 ${card.color}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-extrabold text-white tracking-tight">{card.value}</div>
            <div className="text-xs text-gray-400 mt-1">{card.subtitle}</div>
            
            {/* Micro Progress Line */}
            <div className="w-full h-1 bg-gray-900 rounded-full mt-3 overflow-hidden">
              <div
                style={{ width: `${card.progressPct}%` }}
                className={`h-full rounded-full ${card.color.replace('text-', 'bg-')}`}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
