import React, { useState } from 'react';
import { Search, Filter, CheckCircle, AlertCircle, HelpCircle } from 'lucide-react';

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
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><CheckCircle className="w-3 h-3"/> Matched</span>;
      case 'MISSING_PAYMENT':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20"><AlertCircle className="w-3 h-3"/> Missing Payment</span>;
      case 'MISSING_ORDER':
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20"><HelpCircle className="w-3 h-3"/> Missing Order</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-800 text-gray-400">{status}</span>;
    }
  };

  return (
    <div className="glass-panel p-6 mb-8 border border-gray-800">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4 pb-3 border-b border-gray-800">
        <div>
          <h2 className="text-base font-semibold text-white">Reconciliation Funnel Records</h2>
          <p className="text-xs text-gray-400">Deterministic order-to-settlement match audit manifest</p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Search */}
          <div className="relative flex-1 sm:flex-initial">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Order ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full sm:w-48 pl-9 pr-3 py-1.5 rounded-xl bg-gray-900 border border-gray-800 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Filter tabs */}
          <div className="flex bg-gray-900 p-1 rounded-xl border border-gray-800 text-xs">
            <button
              onClick={() => setFilter('ALL')}
              className={`px-3 py-1 rounded-lg font-medium transition ${filter === 'ALL' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              All ({reconciliation.records.length})
            </button>
            <button
              onClick={() => setFilter('MATCHED')}
              className={`px-3 py-1 rounded-lg font-medium transition ${filter === 'MATCHED' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Matched ({reconciliation.matched_count})
            </button>
            <button
              onClick={() => setFilter('MISSING_PAYMENT')}
              className={`px-3 py-1 rounded-lg font-medium transition ${filter === 'MISSING_PAYMENT' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Missing Payment ({reconciliation.missing_payment_count})
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-900/80 text-gray-400 sticky top-0 uppercase tracking-wider text-[10px]">
            <tr>
              <th className="p-3">Order ID / Key</th>
              <th className="p-3">Order Status</th>
              <th className="p-3">Payment Settlement Status</th>
              <th className="p-3">Settlement Amount</th>
              <th className="p-3">Match Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {filteredRecords.map((r, idx) => (
              <tr key={idx} className="hover:bg-gray-800/40 transition">
                <td className="p-3 font-mono font-medium text-blue-400">{r.order_id}</td>
                <td className="p-3 text-gray-300">{r.order_status || '—'}</td>
                <td className="p-3 text-gray-300">{r.payment_status || '—'}</td>
                <td className="p-3 font-medium text-gray-100">
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
