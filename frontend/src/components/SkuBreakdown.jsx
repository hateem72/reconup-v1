import React, { useState } from 'react';
import { Package, TrendingUp, TrendingDown, Tag } from 'lucide-react';

export default function SkuBreakdown({ skuBreakdown }) {
  const [search, setSearch] = useState('');

  if (!skuBreakdown || Object.keys(skuBreakdown).length === 0) return null;

  const skus = Object.keys(skuBreakdown).filter(sku =>
    !search || sku.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="glass-panel p-6 mb-8 border border-gray-800">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4 pb-3 border-b border-gray-800">
        <div>
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-400" />
            SKU Profit & Deduction Analysis
          </h2>
          <p className="text-xs text-gray-400">Unit cost breakdown, return penalties, claims, and net margins per SKU</p>
        </div>

        <input
          type="text"
          placeholder="Filter SKU..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 rounded-xl bg-gray-900 border border-gray-800 text-xs text-gray-200 focus:outline-none focus:border-indigo-500 w-full sm:w-48"
        />
      </div>

      <div className="overflow-x-auto max-h-80 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-900/90 text-gray-400 sticky top-0 uppercase tracking-wider text-[10px]">
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
          <tbody className="divide-y divide-gray-800/60 font-mono">
            {skus.map((skuId) => {
              const b = skuBreakdown[skuId];
              return (
                <tr key={skuId} className="hover:bg-gray-800/40 transition">
                  <td className="p-3 font-bold text-indigo-400 flex items-center gap-1.5">
                    <Tag className="w-3.5 h-3.5 text-gray-500" />
                    {skuId}
                  </td>
                  <td className="p-3 text-gray-200">
                    {b.deliveredCount} <span className="text-[10px] text-gray-500">(₹{b.deliveredSales.toFixed(2)})</span>
                  </td>
                  <td className="p-3 text-amber-400">{b.returnCount}</td>
                  <td className="p-3 text-gray-400">{b.rtoCount}</td>
                  <td className="p-3 text-gray-300">₹{b.costPerUnit.toFixed(2)}</td>
                  <td className="p-3 text-gray-300">₹{b.totalCost.toFixed(2)}</td>
                  <td className="p-3 text-rose-400">₹{b.returnPenalty.toFixed(2)}</td>
                  <td className="p-3 text-emerald-400">₹{b.claim.toFixed(2)}</td>
                  <td className="p-3 text-amber-400">₹{b.affiliateFees.toFixed(2)}</td>
                  <td className="p-3 font-bold">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs ${b.isProfitable ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                      {b.isProfitable ? <TrendingUp className="w-3 h-3"/> : <TrendingDown className="w-3 h-3"/>}
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
