import React, { useState } from 'react';
import { Search, Filter, CheckCircle2, XCircle, RotateCcw, PackageX, Truck, PackageCheck, AlertTriangle, Clock, Layers, ArrowUpRight, DollarSign, Code } from 'lucide-react';
import RawJsonModal from './RawJsonModal';

export default function ReconciliationView({ reconciliation }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [expandedRowId, setExpandedRowId] = useState(null);
  const [showJsonModal, setShowJsonModal] = useState(false);

  if (!reconciliation) {
    return (
      <div className="rounded-2xl bg-white border border-slate-200 p-8 text-center text-slate-500 text-xs">
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

  // Compute Operational Lifecycle Status Counts
  const statusCounts = {
    Delivered: 0,
    Cancelled: 0,
    Return: 0,
    RTO: 0,
    Other: 0
  };

  allRecords.forEach(r => {
    const rawSt = (r.status || r.live_order_status || r.eventStatus || r.raw_status || '').toLowerCase().trim();
    if (rawSt.includes('deliver')) {
      statusCounts.Delivered += 1;
    } else if (rawSt.includes('cancel')) {
      statusCounts.Cancelled += 1;
    } else if (rawSt.includes('rto') || rawSt.includes('return to origin')) {
      statusCounts.RTO += 1;
    } else if (rawSt.includes('return') || rawSt.includes('exchange')) {
      statusCounts.Return += 1;
    } else if (rawSt) {
      statusCounts.Other += 1;
    }
  });

  const filteredRecords = allRecords.filter(r => {
    const oid = (r.orderId || r.order_id || '').toLowerCase();
    const pDetails = (r.productDetails || r.sku || '').toLowerCase();
    const rawSt = (r.status || r.live_order_status || r.eventStatus || r.raw_status || '').toLowerCase();

    const matchesSearch = oid.includes(searchTerm.toLowerCase()) || pDetails.includes(searchTerm.toLowerCase());

    let matchesFilter = true;
    if (statusFilter === 'ALL') {
      matchesFilter = true;
    } else if (['MATCHED', 'MISSING_PAYMENT', 'HISTORICAL_PAYMENT'].includes(statusFilter)) {
      matchesFilter = r.statusType === statusFilter;
    } else if (statusFilter === 'DELIVERED') {
      matchesFilter = rawSt.includes('deliver');
    } else if (statusFilter === 'CANCELLED') {
      matchesFilter = rawSt.includes('cancel');
    } else if (statusFilter === 'RETURN') {
      matchesFilter = rawSt.includes('return') || rawSt.includes('exchange');
    } else if (statusFilter === 'RTO') {
      matchesFilter = rawSt.includes('rto') || rawSt.includes('return to origin');
    }

    return matchesSearch && matchesFilter;
  });

  const totalOrders = rawRec.totalOrders || reconciliation.total_records || matchedList.length;
  const matchRate = rawRec.matchRate || reconciliation.match_rate || 0;

  return (
    <div className="space-y-6">
      <RawJsonModal
        title="Node 5 Order Reconciliation & Net Payout Database"
        data={reconciliation}
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
      />

      {/* Executive Funnel & KPI Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">
          <span className="text-xs font-bold text-slate-500 block mb-1">Master Order Anchors</span>
          <div className="text-2xl font-black text-slate-900 font-mono">{totalOrders}</div>
          <span className="text-[10px] text-slate-500 font-medium mt-1 block">Master Manifest Orders</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-emerald-200 shadow-xs">
          <span className="text-xs font-bold text-emerald-700 block mb-1">Matched Orders</span>
          <div className="text-2xl font-black text-emerald-600 font-mono">{matchedList.length}</div>
          <span className="text-[10px] text-emerald-700/80 font-medium mt-1 block">Match Rate: {matchRate}%</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-amber-200 shadow-xs">
          <span className="text-xs font-bold text-amber-700 block mb-1">Unsettled Orders</span>
          <div className="text-2xl font-black text-amber-600 font-mono">{missingInPmtList.length}</div>
          <span className="text-[10px] text-amber-700/80 font-medium mt-1 block">Missing Settlement Entry</span>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-cyan-200 shadow-xs">
          <span className="text-xs font-bold text-cyan-700 block mb-1">Historical Payments</span>
          <div className="text-2xl font-black text-cyan-600 font-mono">{historicalList.length}</div>
          <span className="text-[10px] text-cyan-700/80 font-medium mt-1 block">Previous Month Payouts</span>
        </div>
      </div>

      {/* Operational Order Status Lifecycle Summary Breakdown */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center gap-2">
            <PackageCheck className="w-4 h-4 text-blue-600" />
            Operational Order Status Breakdown
          </h4>
          <span className="text-[11px] text-slate-500 font-mono">
            Click any status card to filter database records below
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-3">
          {/* Delivered Card */}
          <button
            onClick={() => setStatusFilter(statusFilter === 'DELIVERED' ? 'ALL' : 'DELIVERED')}
            className={`p-3.5 rounded-xl border text-left transition cursor-pointer ${
              statusFilter === 'DELIVERED'
                ? 'bg-emerald-100 border-emerald-500 shadow-xs'
                : 'bg-emerald-50/60 border-emerald-200 hover:bg-emerald-100/70'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-extrabold text-emerald-900">Delivered</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-xl font-black text-emerald-700 font-mono">{statusCounts.Delivered}</div>
            <span className="text-[10px] text-emerald-800 font-semibold block mt-0.5">Successful Fulfillments</span>
          </button>

          {/* Cancelled Card */}
          <button
            onClick={() => setStatusFilter(statusFilter === 'CANCELLED' ? 'ALL' : 'CANCELLED')}
            className={`p-3.5 rounded-xl border text-left transition cursor-pointer ${
              statusFilter === 'CANCELLED'
                ? 'bg-rose-100 border-rose-500 shadow-xs'
                : 'bg-rose-50/60 border-rose-200 hover:bg-rose-100/70'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-extrabold text-rose-900">Cancelled</span>
              <XCircle className="w-4 h-4 text-rose-600" />
            </div>
            <div className="text-xl font-black text-rose-700 font-mono">{statusCounts.Cancelled}</div>
            <span className="text-[10px] text-rose-800 font-semibold block mt-0.5">Pre-Dispatch Cancelled</span>
          </button>

          {/* Customer Return Card */}
          <button
            onClick={() => setStatusFilter(statusFilter === 'RETURN' ? 'ALL' : 'RETURN')}
            className={`p-3.5 rounded-xl border text-left transition cursor-pointer ${
              statusFilter === 'RETURN'
                ? 'bg-amber-100 border-amber-500 shadow-xs'
                : 'bg-amber-50/60 border-amber-200 hover:bg-amber-100/70'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-extrabold text-amber-900">Customer Return</span>
              <RotateCcw className="w-4 h-4 text-amber-600" />
            </div>
            <div className="text-xl font-black text-amber-700 font-mono">{statusCounts.Return}</div>
            <span className="text-[10px] text-amber-800 font-semibold block mt-0.5">Returned by Customer</span>
          </button>

          {/* RTO Card */}
          <button
            onClick={() => setStatusFilter(statusFilter === 'RTO' ? 'ALL' : 'RTO')}
            className={`p-3.5 rounded-xl border text-left transition cursor-pointer ${
              statusFilter === 'RTO'
                ? 'bg-purple-100 border-purple-500 shadow-xs'
                : 'bg-purple-50/60 border-purple-200 hover:bg-purple-100/70'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-extrabold text-purple-900">RTO (Return to Origin)</span>
              <PackageX className="w-4 h-4 text-purple-600" />
            </div>
            <div className="text-xl font-black text-purple-700 font-mono">{statusCounts.RTO}</div>
            <span className="text-[10px] text-purple-800 font-semibold block mt-0.5">Undelivered / RTO</span>
          </button>

          {/* Other / Shipped Card */}
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-left">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-extrabold text-slate-800">Shipped / Other</span>
              <Truck className="w-4 h-4 text-slate-500" />
            </div>
            <div className="text-xl font-black text-slate-700 font-mono">{statusCounts.Other}</div>
            <span className="text-[10px] text-slate-500 font-semibold block mt-0.5">In Transit / Fee / Claim</span>
          </div>
        </div>
      </div>

      {/* Main Reconciliation Data Table */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-200">
          <div>
            <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-600" />
              Complete Deterministic Order Settlement Database
            </h3>
            <p className="text-xs text-slate-500 font-medium">
              Aggregated Net Payout Amounts per Order ID across multi-event payout lines
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={() => setShowJsonModal(true)}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-mono font-bold flex items-center gap-1.5 transition shadow-xs cursor-pointer shrink-0"
              title="View Raw Backend JSON Payload"
            >
              <Code className="w-3.5 h-3.5 text-cyan-400" />
              <span>Raw JSON Data</span>
            </button>

            {/* Search Box */}
            <div className="relative flex-1 sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search Order ID or SKU..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            {/* Filter Dropdown */}
            <div className="relative shrink-0">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="py-2 px-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 font-bold focus:outline-none focus:border-blue-500 cursor-pointer"
              >
                <option value="ALL">All Statuses ({allRecords.length})</option>
                <option value="MATCHED">Matched ({matchedList.length})</option>
                <option value="MISSING_PAYMENT">Unsettled ({missingInPmtList.length})</option>
                <option value="HISTORICAL_PAYMENT">Historical ({historicalList.length})</option>
                <option value="DELIVERED">Delivered ({statusCounts.Delivered})</option>
                <option value="CANCELLED">Cancelled ({statusCounts.Cancelled})</option>
                <option value="RETURN">Customer Return ({statusCounts.Return})</option>
                <option value="RTO">RTO ({statusCounts.RTO})</option>
              </select>
            </div>
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-[11px] font-extrabold text-slate-500 uppercase tracking-wider bg-slate-50/50">
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Status / Event</th>
                <th className="py-3 px-4">SKU / Product Details</th>
                <th className="py-3 px-4 text-right">Net Payout (₹)</th>
                <th className="py-3 px-4 text-center">Match State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs font-mono">
              {filteredRecords.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400 font-sans font-medium">
                    No order settlement records match the active search or status filter.
                  </td>
                </tr>
              ) : (
                filteredRecords.map((row, rIdx) => {
                  const oid = row.orderId || row.order_id || 'N/A';
                  const status = row.status || row.live_order_status || row.eventStatus || 'DELIVERED';
                  const sku = row.productDetails || row.sku || 'N/A';
                  const payout = row.netPayout !== undefined ? row.netPayout : (row.amount || 0);

                  const isMatched = row.statusType === 'MATCHED';
                  const isMissingPmt = row.statusType === 'MISSING_PAYMENT';

                  return (
                    <tr key={rIdx} className="hover:bg-slate-50/80 transition">
                      <td className="py-3 px-4 font-bold text-slate-900">{oid}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-800 border border-slate-200">
                          {status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-700 truncate max-w-xs">{sku}</td>
                      <td className={`py-3 px-4 text-right font-black ${payout < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                        ₹{Number(payout).toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {isMatched ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                            <CheckCircle2 className="w-3 h-3" />
                            MATCHED
                          </span>
                        ) : isMissingPmt ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            <AlertTriangle className="w-3 h-3" />
                            UNSETTLED
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold bg-cyan-100 text-cyan-800 border border-cyan-300">
                            <Clock className="w-3 h-3" />
                            HISTORICAL
                          </span>
                        )}
                      </td>
                    </tr>
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
