import React, { useState, useEffect } from 'react';
import { CheckCircle2, Bot, ArrowRight, RefreshCw, Play, Tag } from 'lucide-react';

const CANONICAL_CATEGORIES = [
  'Delivered',
  'Return',
  'RTO',
  'Cancelled',
  'Shipped',
  'Exchange',
  'Claim',
  'Compensation',
  'Deduction'
];

export default function StatusNormalizationView({ batchId, onNext, onReprocessSuccess }) {
  const [nodeDetails, setNodeDetails] = useState(null);
  const [statusOverrides, setStatusOverrides] = useState({});
  const [isReprocessing, setIsReprocessing] = useState(false);

  useEffect(() => {
    if (!batchId) return;

    const fetchDetails = async () => {
      try {
        const res = await fetch(`/api/batches/${batchId}/node-details`);
        if (res.ok) {
          const data = await res.json();
          setNodeDetails(data);
          const initialOverrides = data.human_overrides?.status_overrides || {};
          setStatusOverrides(initialOverrides);
        }
      } catch (err) {
        console.error("Error fetching status details:", err);
      }
    };

    fetchDetails();
  }, [batchId]);

  const handleCategorySelect = (rawStatus, category) => {
    setStatusOverrides(prev => ({
      ...prev,
      [rawStatus]: category
    }));
  };

  const handleApplyOverridesAndReprocess = async () => {
    if (!batchId) return;
    setIsReprocessing(true);
    try {
      const res = await fetch(`/api/batches/${batchId}/reprocess`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_node: 3.0,
          status_mapping_overrides: statusOverrides
        })
      });
      const data = await res.json();
      if (res.ok && onReprocessSuccess) {
        await onReprocessSuccess(data);
        onNext();
      }
    } catch (err) {
      console.error("Error reprocessing from Node 3:", err);
    } finally {
      setIsReprocessing(false);
    }
  };

  const statusMappings = nodeDetails?.node3?.status_mappings || {};
  const rawStatusEntries = Object.entries(statusMappings);

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 border border-blue-200">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 4: Node 3 Status Normalization & Human Control</h2>
            <p className="text-xs text-slate-500 font-medium">
              Autonomous Agent <strong className="text-blue-700">StatusNormalizationAgent</strong> categorizes unique raw status strings into canonical lifecycle states.
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
          {rawStatusEntries.length} Unique Raw Statuses Extracted
        </span>
      </div>

      <div className="space-y-4">
        <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider">
          Extracted Unique Raw Status Strings & Canonical Categorizations:
        </h3>

        {rawStatusEntries.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs font-bold bg-slate-50 rounded-xl border border-slate-200">
            No status strings extracted yet. Please process datasets in Step 1.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {rawStatusEntries.map(([rawStatus, info]) => {
              const aiCat = typeof info === 'object' ? (info.canonical_category || rawStatus) : info;
              const activeOverride = statusOverrides[rawStatus];
              const currentCategory = activeOverride || aiCat;
              const isOverridden = activeOverride !== undefined && activeOverride !== aiCat;

              return (
                <div
                  key={rawStatus}
                  className={`p-4 rounded-xl border space-y-2.5 transition ${
                    isOverridden ? 'bg-amber-50/50 border-amber-300' : 'bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Tag className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                      <span className="text-xs font-mono font-extrabold text-slate-900">"{rawStatus}"</span>
                    </div>

                    {isOverridden && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-900 border border-amber-300">
                        Human Override
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-600 shrink-0">Canonical Category:</span>
                    <select
                      value={currentCategory}
                      onChange={(e) => handleCategorySelect(rawStatus, e.target.value)}
                      className="w-full py-1.5 px-2.5 rounded-lg bg-white border border-slate-200 text-xs font-mono font-extrabold text-slate-900 focus:outline-none focus:border-blue-500"
                    >
                      {CANONICAL_CATEGORIES.map(cat => (
                        <option key={cat} value={cat}>
                          {cat}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200">
        <button
          onClick={handleApplyOverridesAndReprocess}
          disabled={isReprocessing}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2 transition disabled:opacity-50"
        >
          {isReprocessing ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Reprocessing Pipeline from Node 3...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Run From Node 3 (Apply Status Normalization Overrides)</span>
            </>
          )}
        </button>

        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2 transition"
        >
          <span>Proceed to Step 5: Order Reconciliation Database</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
