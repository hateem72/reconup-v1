import React from 'react';
import { DollarSign, CheckCircle2, AlertTriangle, Zap, TrendingUp, Layers } from 'lucide-react';

export default function MetricsCards({ metrics, summary }) {
  if (!metrics) return null;

  const cards = [
    {
      title: "Match Rate",
      value: `${metrics.match_rate}%`,
      subtitle: `${metrics.records_matched} / ${metrics.total_records} records matched`,
      icon: CheckCircle2,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10 border-emerald-500/20"
    },
    {
      title: "Net Profit / Loss",
      value: `₹${(summary?.totalProfit ?? metrics.total_profit ?? 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`,
      subtitle: `Revenue: ₹${(summary?.totalDeliveredSales ?? metrics.total_revenue ?? 0).toLocaleString('en-IN')}`,
      icon: TrendingUp,
      color: (metrics.total_profit >= 0) ? "text-emerald-400" : "text-rose-400",
      bg: (metrics.total_profit >= 0) ? "bg-emerald-500/10 border-emerald-500/20" : "bg-rose-500/10 border-rose-500/20"
    },
    {
      title: "Unresolved Exceptions",
      value: metrics.unresolved_exceptions,
      subtitle: `Exposure: ₹${metrics.unresolved_financial_exposure?.toLocaleString('en-IN') || 0}`,
      icon: AlertTriangle,
      color: metrics.unresolved_exceptions > 0 ? "text-amber-400" : "text-gray-400",
      bg: metrics.unresolved_exceptions > 0 ? "bg-amber-500/10 border-amber-500/20" : "bg-gray-800 border-gray-700"
    },
    {
      title: "Throughput & Speed",
      value: `${metrics.throughput_records_per_sec} rec/s`,
      subtitle: `Processing time: ${metrics.processing_time_ms} ms`,
      icon: Zap,
      color: "text-blue-400",
      bg: "bg-blue-500/10 border-blue-500/20"
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className={`p-5 rounded-2xl border ${card.bg} backdrop-blur-md transition hover:scale-[1.01]`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">{card.title}</span>
              <div className={`p-2 rounded-xl bg-gray-900/60 ${card.color}`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">{card.value}</div>
            <div className="text-xs text-gray-400 mt-1">{card.subtitle}</div>
          </div>
        );
      })}
    </div>
  );
}
