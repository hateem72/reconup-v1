import React, { useEffect, useState } from 'react';
import { X, DollarSign, Save, Tag, AlertTriangle, CheckCircle2 } from 'lucide-react';

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

      // Combine DB costs with SKUs present in current batch
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-3xl p-6 border border-gray-800 rounded-2xl shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            <div>
              <h2 className="text-base font-extrabold text-white">Configure Product Cost Prices & Packaging Costs</h2>
              <p className="text-xs text-gray-400">Set cost price per unit to enable accurate profit & loss calculations</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        {saveSuccess && (
          <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-xl flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            Costs saved to SQLite database! Recalculated batch profit automatically.
          </div>
        )}

        <div className="mt-4 max-h-96 overflow-y-auto pr-1">
          <table className="w-full text-left text-xs">
            <thead className="bg-gray-900 text-gray-400 sticky top-0 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="p-3">SKU ID</th>
                <th className="p-3">Product Cost Price (₹)</th>
                <th className="p-3">Packaging Cost (₹)</th>
                <th className="p-3">Total Unit Cost (₹)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {Object.keys(costInputs).map((sku) => {
                const item = costInputs[sku] || { cost_price: 0, packaging_cost: 0 };
                const totalUnit = (item.cost_price || 0) + (item.packaging_cost || 0);
                const isZero = totalUnit <= 0;

                return (
                  <tr key={sku} className="hover:bg-gray-800/40">
                    <td className="p-3 font-mono font-bold text-indigo-400 flex items-center gap-2">
                      <Tag className="w-3.5 h-3.5 text-gray-500" />
                      {sku}
                      {isZero && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
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
                        className="w-28 px-3 py-1.5 rounded-lg bg-gray-950 border border-gray-800 text-xs text-white focus:border-emerald-500 focus:outline-none font-mono"
                      />
                    </td>
                    <td className="p-3">
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={item.packaging_cost}
                        onChange={(e) => handleChange(sku, 'packaging_cost', e.target.value)}
                        className="w-28 px-3 py-1.5 rounded-lg bg-gray-950 border border-gray-800 text-xs text-white focus:border-emerald-500 focus:outline-none font-mono"
                      />
                    </td>
                    <td className="p-3 font-mono font-bold text-emerald-400">
                      ₹{totalUnit.toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-800 flex items-center justify-between">
          <p className="text-xs text-gray-400">
            Total Unit Cost = Product Cost Price + Packaging Cost
          </p>
          <button
            onClick={handleSave}
            disabled={loading}
            className="px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg glow-emerald flex items-center gap-2 disabled:opacity-50 transition"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Saving & Recalculating...' : 'Save Costs & Recalculate Profit'}
          </button>
        </div>
      </div>
    </div>
  );
}
