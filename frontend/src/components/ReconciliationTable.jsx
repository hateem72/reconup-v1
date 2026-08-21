import React, { useState } from 'react';
import { Search, CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';

export default function ReconciliationTable({ reconciliation }) {
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  if (!reconciliation || !reconciliation.records) return null;

  const filteredRecords = reconciliation.records.filter(r => {
    const matchesFilter = filter === 'ALL' || r.match_status === filter;
    const matchesSearch = !search || r.order_id.toLowerCase().includes(search.toLowerCase()) || (r.payment_status && r.payment_status.toLowerCase().includes(search.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'MATCHED':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200"><CheckCircle className="w-3 h-3"/> Matched</span>;
      case 'MISSING_PAYMENT':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200"><AlertCircle className="w-3 h-3"/> Missing Payment</span>;
      case 'MISSING_ORDER':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200"><HelpCircle className="w-3 h-3"/> Missing Order</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">{status}</span>;
    }
  };

  return (
    <div className="glass-panel p-6 mb-8 border border-slate-200 bg-white shadow-soft">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-base font-extrabold text-slate-900">Step 4: Multi-Source Reconciliation Audit Log</h2>
          <p className="text-xs text-slate-500">Deterministic order-to-settlement match audit manifest</p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Search */}
          <div className="relative flex-1 sm:flex-initial">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Order ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full sm:w-48 pl-9 pr-3 py-1.5 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-blue-600"
            />
          </div>

          {/* Filter tabs */}
          <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-3 py-1 rounded-lg font-bold transition ${filter === 'ALL' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
            >
              All ({reconciliation.records.length})
            </button>
            <button
              onClick={() => setFilter('MATCHED')}
              className={`px-3 py-1 rounded-lg font-bold transition ${filter === 'MATCHED' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Matched ({reconciliation.matched_count})
            </button>
            <button
              onClick={() => setFilter('MISSING_PAYMENT')}
              className={`px-3 py-1 rounded-lg font-bold transition ${filter === 'MISSING_PAYMENT' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Missing Payment ({reconciliation.missing_payment_count})
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-100 text-slate-700 sticky top-0 uppercase tracking-wider text-[10px] font-bold">
            <tr>
              <th className="p-3">Order ID / Key</th>
              <th className="p-3">Order Status</th>
              <th className="p-3">Payment Settlement Status</th>
              <th className="p-3">Settlement Amount</th>
              <th className="p-3">Match Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {filteredRecords.map((r, idx) => (
              <tr key={idx} className="hover:bg-slate-50 transition font-medium">
                <td className="p-3 font-mono font-bold text-blue-700">{r.order_id}</td>
                <td className="p-3 text-slate-800">{r.order_status || '—'}</td>
                <td className="p-3 text-slate-800">{r.payment_status || '—'}</td>
                <td className="p-3 font-mono font-bold text-slate-900">
                  {r.payment_amount ? `₹${r.payment_amount.toFixed(2)}` : '₹0.00'}
                </td>
                <td className="p-3">{getStatusBadge(r.match_status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
