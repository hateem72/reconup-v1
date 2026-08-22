import React, { useState } from 'react';
import { Search, Filter, CheckCircle2, AlertTriangle, Clock, Layers, ArrowUpRight, DollarSign } from 'lucide-react';

export default function ReconciliationView({ reconciliation }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [expandedRowId, setExpandedRowId] = useState(null);

  if (!reconciliation) {
    return (
      <div className="rounded-2xl bg-slate-900 border border-slate-800 p-8 text-center text-slate-400 text-xs">
        No reconciliation data available. Please upload datasets or click "Run Synthetic Demo".
      </div>
    );
  }

  const rawRec = reconciliation.raw_reconciliation || {};
  const matchedList = rawRec.matched || [];
  const missingInPmtList = rawRec.missingInPayment || [];
  const historicalList = rawRec.missingInOrder || [];

  const allRecords = [
    ...matchedList.map(m => ({ ...m, statusType: 'MATCHED' })),
    ...missingInPmtList.map(m => ({ ...m, statusType: 'MISSING_PAYMENT' })),
    ...historicalList.map(m => ({ ...m, statusType: 'HISTORICAL_PAYMENT' }))
  ];

  const filteredRecords = allRecords.filter(r => {
    const oid = (r.orderId || r.order_id || '').toLowerCase();
    const pDetails = (r.productDetails || r.sku || '').toLowerCase();
    const matchesSearch = oid.includes(searchTerm.toLowerCase()) || pDetails.includes(searchTerm.toLowerCase());
    const matchesFilter = statusFilter === 'ALL' || r.statusType === statusFilter;
    return matchesSearch && matchesFilter;
  });

  const totalOrders = rawRec.totalOrders || reconciliation.total_records || matchedList.length;
  const matchRate = rawRec.matchRate || reconciliation.match_rate || 0;

  return (
    <div className="space-y-6">
      {/* Executive Funnel & KPI Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl">
          <span className="text-xs font-semibold text-slate-400 block mb-1">Master Order Anchors</span>
          <div className="text-2xl font-black text-white font-mono">{totalOrders}</div>
          <span className="text-[10px] text-slate-500 mt-1 block">Master Manifest Orders</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-emerald-500/30 bg-emerald-500/5 shadow-xl">
          <span className="text-xs font-semibold text-emerald-400 block mb-1">Matched Orders</span>
          <div className="text-2xl font-black text-emerald-400 font-mono">{matchedList.length}</div>
          <span className="text-[10px] text-emerald-500/80 mt-1 block">Match Rate: {matchRate}%</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-amber-500/30 bg-amber-500/5 shadow-xl">
          <span className="text-xs font-semibold text-amber-400 block mb-1">Unsettled Orders</span>
          <div className="text-2xl font-black text-amber-400 font-mono">{missingInPmtList.length}</div>
          <span className="text-[10px] text-amber-500/80 mt-1 block">Missing Settlement Entry</span>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900 border border-cyan-500/30 bg-cyan-500/5 shadow-xl">
          <span className="text-xs font-semibold text-cyan-400 block mb-1">Historical Payments</span>
          <div className="text-2xl font-black text-cyan-400 font-mono">{historicalList.length}</div>
          <span className="text-[10px] text-cyan-500/80 mt-1 block">Previous Month Payouts</span>
        </div>
      </div>

      {/* Main Reconciliation Data Table */}
      <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-extrabold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              Complete Deterministic Order Settlement Database
            </h3>
            <p className="text-xs text-slate-400">
              Aggregated Net Payout Amounts per Order ID across multi-event payout lines
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Search Box */}
            <div className="relative flex-1 sm:w-64">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search Order ID or SKU..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            {/* Filter Selector */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="py-2 px-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-medium focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Records ({allRecords.length})</option>
              <option value="MATCHED">Matched ({matchedList.length})</option>
              <option value="MISSING_PAYMENT">Unsettled ({missingInPmtList.length})</option>
              <option value="HISTORICAL_PAYMENT">Historical ({historicalList.length})</option>
            </select>
          </div>
        </div>

        {/* Table View */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold bg-slate-950/60">
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Order Date</th>
                <th className="py-3 px-4">Product SKU</th>
                <th className="py-3 px-4">Qty</th>
                <th className="py-3 px-4">Order Status</th>
                <th className="py-3 px-4">Payment Events</th>
                <th className="py-3 px-4 text-right">Net Payout Amount</th>
                <th className="py-3 px-4 text-center">Match Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-500">
                    No matching reconciliation records found for '{searchTerm}'.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((r, idx) => {
                  const oid = r.orderId || r.order_id;
                  const isExpanded = expandedRowId === oid;

                  return (
                    <React.Fragment key={idx}>
                      <tr
                        onClick={() => setExpandedRowId(isExpanded ? null : oid)}
                        className="hover:bg-slate-800/40 cursor-pointer transition"
                      >
                        <td className="py-3 px-4 font-bold text-blue-400">{oid}</td>
                        <td className="py-3 px-4 text-slate-400">{r.orderDate || r.order_date || 'N/A'}</td>
                        <td className="py-3 px-4 text-slate-200">{r.productDetails || r.sku || 'N/A'}</td>
                        <td className="py-3 px-4 text-slate-300">{r.qty || 1}</td>
                        <td className="py-3 px-4 text-slate-300">
                          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-sans font-medium text-[11px]">
                            {r.orderSheetStatus || r.order_status || 'N/A'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-400 truncate max-w-[180px]">
                          {r.paymentStatuses || r.payment_status || 'N/A'}
                        </td>
                        <td className="py-3 px-4 text-right font-bold text-emerald-400">
                          ₹{((r.totalPayment !== undefined ? r.totalPayment : r.payment_amount) || 0).toFixed(2)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          {r.statusType === 'MATCHED' && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                              ✓ MATCHED
                            </span>
                          )}
                          {r.statusType === 'MISSING_PAYMENT' && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                              ⚠ UNSETTLED
                            </span>
                          )}
                          {r.statusType === 'HISTORICAL_PAYMENT' && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                              🕒 HISTORICAL
                            </span>
                          )}
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="bg-slate-950/90 border-b border-slate-800">
                          <td colSpan={8} className="p-4 text-xs font-sans">
                            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                              <h4 className="text-xs font-bold text-white flex items-center gap-2">
                                <DollarSign className="w-4 h-4 text-emerald-400" />
                                Multi-Event Net Payout Aggregation Breakdown for Order [{oid}]
                              </h4>
                              <p className="text-[11px] text-slate-400">
                                Status Events Combined: <strong className="text-cyan-300">{r.paymentStatuses || 'N/A'}</strong>
                              </p>
                              <div className="flex justify-between items-center text-xs font-mono pt-2 border-t border-slate-800">
                                <span className="text-slate-400">Final Aggregated Net Settlement Amount:</span>
                                <span className="text-emerald-400 font-extrabold text-sm">
                                  ₹{((r.totalPayment !== undefined ? r.totalPayment : r.payment_amount) || 0).toFixed(2)}
                                </span>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
