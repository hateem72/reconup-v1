import React, { useEffect, useState } from 'react';
import { X, DollarSign, Save, Tag, CheckCircle2 } from 'lucide-react';

export default function CostPriceModal({ isOpen, onClose, batchId, skuBreakdown, onCostsUpdated }) {
  const [costInputs, setCostInputs] = useState({});
  const [loading, setLoading] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchExistingCosts();
    }
  }, [isOpen, skuBreakdown]);

  const fetchExistingCosts = async () => {
    try {
      const res = await fetch('/api/costs');
      const data = await res.json();
      const dbCostsMap = {};
      (data.costs || []).forEach(c => {
        dbCostsMap[c.sku_id] = {
          cost_price: c.cost_price,
          packaging_cost: c.packaging_cost
        };
      });

      const initialInputs = {};
      const batchSkus = skuBreakdown ? Object.keys(skuBreakdown) : [];
      
      batchSkus.forEach(sku => {
        const existing = dbCostsMap[sku];
        const currentBreakdown = skuBreakdown[sku];
        initialInputs[sku] = {
          cost_price: existing ? existing.cost_price : (currentBreakdown?.costPerUnit || 0),
          packaging_cost: existing ? existing.packaging_cost : 0
        };
      });

      setCostInputs(initialInputs);
    } catch (err) {
      console.error(err);
    }
  };

  const handleChange = (sku, field, value) => {
    setCostInputs(prev => ({
      ...prev,
      [sku]: {
        ...prev[sku],
        [field]: parseFloat(value) || 0
      }
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setSaveSuccess(false);
    try {
      const costList = Object.keys(costInputs).map(sku => ({
        sku_id: sku,
        cost_price: costInputs[sku].cost_price || 0,
        packaging_cost: costInputs[sku].packaging_cost || 0
      }));

      const res = await fetch('/api/costs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          costs: costList,
          batch_id: batchId
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to save costs');

      setSaveSuccess(true);
      if (onCostsUpdated) {
        onCostsUpdated();
      }
      setTimeout(() => {
        setSaveSuccess(false);
        onClose();
      }, 1000);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-3xl p-6 border border-slate-200 rounded-2xl shadow-2xl bg-white">
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700">
              <DollarSign className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900">Step 2: Configure Product Unit Cost Prices</h2>
              <p className="text-xs text-slate-500">Set cost price & packaging cost per unit to calculate deterministic P&L</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {saveSuccess && (
          <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-xl flex items-center gap-2 font-medium">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Unit costs saved to SQLite registry! Recalculated batch P&L automatically.
          </div>
        )}

        <div className="mt-4 max-h-96 overflow-y-auto pr-1">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-600 sticky top-0 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="p-3">SKU ID</th>
                <th className="p-3">Product Cost Price (₹)</th>
                <th className="p-3">Packaging Cost (₹)</th>
                <th className="p-3">Total Unit Cost (₹)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {Object.keys(costInputs).map((sku) => {
                const item = costInputs[sku] || { cost_price: 0, packaging_cost: 0 };
                const totalUnit = (item.cost_price || 0) + (item.packaging_cost || 0);
                const isZero = totalUnit <= 0;

                return (
                  <tr key={sku} className="hover:bg-slate-50 transition">
                    <td className="p-3 font-mono font-bold text-indigo-700 flex items-center gap-2">
                      <Tag className="w-3.5 h-3.5 text-slate-400" />
                      {sku}
                      {isZero && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200">
                          Cost Missing
                        </span>
                      )}
                    </td>
                    <td className="p-3">
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={item.cost_price}
                        onChange={(e) => handleChange(sku, 'cost_price', e.target.value)}
                        className="w-28 px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-xs text-slate-900 focus:border-blue-600 focus:outline-none font-mono"
                      />
                    </td>
                    <td className="p-3">
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={item.packaging_cost}
                        onChange={(e) => handleChange(sku, 'packaging_cost', e.target.value)}
                        className="w-28 px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-xs text-slate-900 focus:border-blue-600 focus:outline-none font-mono"
                      />
                    </td>
                    <td className="p-3 font-mono font-bold text-emerald-700">
                      ₹{totalUnit.toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-200 flex items-center justify-between">
          <p className="text-xs text-slate-500 font-medium">
            Total Unit Cost = Product Cost Price + Packaging Cost
          </p>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md flex items-center gap-2 disabled:opacity-50 transition"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Saving & Recalculating...' : 'Save Costs & Recalculate Profit'}
          </button>
        </div>
      </div>
    </div>
  );
}
