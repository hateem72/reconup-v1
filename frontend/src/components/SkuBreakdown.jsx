import React, { useState } from 'react';
import { Package, TrendingUp, TrendingDown, Tag } from 'lucide-react';

export default function SkuBreakdown({ skuBreakdown }) {
  const [search, setSearch] = useState('');

  if (!skuBreakdown || Object.keys(skuBreakdown).length === 0) return null;

  const skus = Object.keys(skuBreakdown).filter(sku =>
    !search || sku.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 mb-8 border border-slate-200 bg-white shadow-soft">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-600" />
            SKU Profit Margin & Deduction Breakdown
          </h2>
          <p className="text-xs text-slate-500">Unit cost breakdown, return penalties, claims, and net margins per SKU</p>
        </div>

        <input
          type="text"
          placeholder="Filter SKU..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-indigo-600 w-full sm:w-48"
        />
      </div>

      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-100 text-slate-700 sticky top-0 uppercase tracking-wider text-[10px] font-bold">
            <tr>
              <th className="p-3">SKU ID</th>
              <th className="p-3">Delivered</th>
              <th className="p-3">Returns</th>
              <th className="p-3">RTO</th>
              <th className="p-3">Unit Cost</th>
              <th className="p-3">Total Cost</th>
              <th className="p-3">Return Penalty</th>
              <th className="p-3">Claim</th>
              <th className="p-3">Affiliate Fee</th>
              <th className="p-3">Net Profit</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 font-mono">
            {skus.map((skuId) => {
              const b = skuBreakdown[skuId];
              return (
                <tr key={skuId} className="hover:bg-slate-50 transition">
                  <td className="p-3 font-bold text-indigo-700 flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5 text-slate-400" />
                    {skuId}
                  </td>
                  <td className="p-3 text-slate-800 font-sans">
                    {b.deliveredCount} <span className="text-[10px] text-slate-500 font-mono">(₹{b.deliveredSales.toFixed(2)})</span>
                  </td>
                  <td className="p-3 text-amber-700 font-bold">{b.returnCount}</td>
                  <td className="p-3 text-slate-500 font-sans">{b.rtoCount}</td>
                  <td className="p-3 text-slate-700 font-bold">₹{b.costPerUnit.toFixed(2)}</td>
                  <td className="p-3 text-slate-700 font-bold">₹{b.totalCost.toFixed(2)}</td>
                  <td className="p-3 text-rose-600 font-bold">₹{b.returnPenalty.toFixed(2)}</td>
                  <td className="p-3 text-emerald-700 font-bold">₹{b.claim.toFixed(2)}</td>
                  <td className="p-3 text-amber-700 font-bold">₹{b.affiliateFees.toFixed(2)}</td>
                  <td className="p-3 font-bold">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono font-bold ${b.isProfitable ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'}`}>
                      {b.isProfitable ? <TrendingUp className="w-3 h-3 text-emerald-600"/> : <TrendingDown className="w-3 h-3 text-rose-600"/>}
                      ₹{b.finalProfit.toFixed(2)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
