import React, { useState, useEffect } from 'react';
import { Grid, CheckCircle2, AlertCircle, Bot, ArrowRight, RefreshCw, Play, Code } from 'lucide-react';
import RawJsonModal from './RawJsonModal';
import HumanReviewGuideline from './HumanReviewGuideline';

const getCanonicalFieldsForSheet = (role = '') => {
  const isPayment = role.toUpperCase().includes('PAYMENT') || role.toUpperCase().includes('SETTLEMENT');
  if (isPayment) {
    return [
      { key: 'order_id', label: 'Order ID / Sub Order No', required: true },
      { key: 'amount', label: 'Final Settlement Amount (Payout)', required: true },
      { key: 'status', label: 'Live Order / Event Status', required: true },
      { key: 'payment_date', label: 'Payment / Settlement Date', required: false },
      { key: 'sku', label: 'Supplier SKU / Product ID', required: false },
      { key: 'quantity', label: 'Item Quantity', required: false }
    ];
  }

  return [
    { key: 'order_id', label: 'Order ID / Sub Order No', required: true },
    { key: 'status', label: 'Live Order Status', required: true },
    { key: 'order_date', label: 'Order Placement Date', required: false },
    { key: 'sku', label: 'Supplier SKU / Product ID', required: false },
    { key: 'product_name', label: 'Product Name / Description', required: false },
    { key: 'quantity', label: 'Dispatched Quantity', required: false }
  ];
};

export default function ColumnMappingView({ batchId, onNext, onReprocessSuccess }) {
  const [nodeDetails, setNodeDetails] = useState(null);
  const [columnOverrides, setColumnOverrides] = useState({});
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [showJsonModal, setShowJsonModal] = useState(false);

  useEffect(() => {
    if (!batchId) return;

    const fetchDetails = async () => {
      try {
        const res = await fetch(`/api/batches/${batchId}/node-details`);
        if (res.ok) {
          const data = await res.json();
          setNodeDetails(data);
          const initialOverrides = data.human_overrides?.column_overrides || {};
          setColumnOverrides(initialOverrides);
        }
      } catch (err) {
        console.error("Error fetching column mapping details:", err);
      }
    };

    fetchDetails();
  }, [batchId]);

  const handleColumnSelect = (sheetName, canonicalKey, sourceCol) => {
    setColumnOverrides(prev => ({
      ...prev,
      [sheetName]: {
        ...(prev[sheetName] || {}),
        [canonicalKey]: sourceCol
      }
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
          start_node: 2.0,
          column_mapping_overrides: columnOverrides
        })
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ detail: 'Failed to reprocess from Node 2' }));
        console.error("Error reprocessing from Node 2:", errJson);
        alert(errJson.detail || 'Failed to reprocess from Node 2');
        return;
      }
      const data = await res.json();
      if (onReprocessSuccess) {
        await onReprocessSuccess(data);
        onNext();
      }
    } catch (err) {
      console.error("Error reprocessing from Node 2:", err);
    } finally {
      setIsReprocessing(false);
    }
  };

  const profiles = nodeDetails?.node1?.sheet_profiles || [];
  const mappings = nodeDetails?.node2?.column_mappings || {};
  const retainedSheets = nodeDetails?.node1_5?.retained_datasets || [];

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <RawJsonModal
        title="Node 2 LLM Column Mapping Matrix"
        data={nodeDetails?.node2 || { column_mappings: {} }}
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 border border-blue-200">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 3: Node 2 LLM Column Mapping Matrix & Human Overrides</h2>
            <p className="text-xs text-slate-500 font-medium">
              Autonomous Agent <strong className="text-blue-700">ColumnMappingAgent</strong> maps raw headers to canonical domain schema. Human operator can override any column mapping.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowJsonModal(true)}
            className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-mono font-bold flex items-center gap-1.5 transition shadow-xs cursor-pointer"
            title="View Raw Backend JSON Payload"
          >
            <Code className="w-3.5 h-3.5 text-cyan-400" />
            <span>Raw JSON Data</span>
          </button>

          <span className="px-3 py-1.5 rounded-full text-xs font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
            Schema Fingerprint Cache Active
          </span>
        </div>
      </div>

      <HumanReviewGuideline
        title="Node 2 Schema Mapping Audit Guidelines"
        role="Canonical Field Alignment Verification"
        guidelines={[
          "Review the mapped columns for Order ID / Sub Order No across all active spreadsheets.",
          "Check that Final Settlement Amount is mapped to net payout columns (e.g. 'Final Settlement Amount', 'Net Payout', 'Payment Amount').",
          "Ensure Live Order Status is mapped to operational status fields (e.g. 'Reason for Credit Entry', 'Status', 'Event Status')."
        ]}
        actionHint="If an AI column mapping is inaccurate, select the correct header from the dropdown and click 'Save Overrides & Re-Process from Node 2'."
      />

      <div className="space-y-6">
        {retainedSheets.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs font-bold bg-slate-50 rounded-xl border border-slate-200">
            No retained sheets found to map columns. Please upload files in Step 1.
          </div>
        ) : (
          retainedSheets.map((sheet, idx) => {
            const fname = sheet.filename;
            const sheetProfile = profiles.find(p => p.sheet_name === fname);
            const sourceHeaders = sheetProfile?.exact_headers?.filter(h => h !== 'id') || sheet.headers || [];
            const sheetMapping = mappings[fname] || {};
            const sheetFields = getCanonicalFieldsForSheet(sheet.role || '');

            return (
              <div key={idx} className="p-5 rounded-xl bg-slate-50 border border-slate-200 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                  <div className="flex items-center gap-2">
                    <Grid className="w-4 h-4 text-blue-600" />
                    <span className="text-xs font-extrabold text-slate-900">{fname}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-200 text-slate-800">
                      {sheet.role || 'WORKBOOK SHEET'}
                    </span>
                  </div>

                  <span className="text-xs font-mono text-slate-500 font-semibold">
                    {sourceHeaders.length} Available Headers
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {sheetFields.map((cField) => {
                    const mappedInfo = sheetMapping[cField.key] || (
                      cField.key === 'payment_date' ? sheetMapping['order_date'] : (
                        cField.key === 'order_date' ? sheetMapping['payment_date'] : null
                      )
                    );
                    const aiSourceCol = mappedInfo?.source_column || 'N/A';
                    const activeOverride = columnOverrides[fname]?.[cField.key];
                    const currentSelected = activeOverride !== undefined ? activeOverride : aiSourceCol;
                    const isOverridden = activeOverride !== undefined && activeOverride !== aiSourceCol;

                    return (
                      <div
                        key={cField.key}
                        className={`p-3 rounded-lg border bg-white space-y-2 ${
                          isOverridden ? 'border-amber-300 bg-amber-50/40' : 'border-slate-200'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-900">
                            {cField.label} {cField.required && <span className="text-rose-500">*</span>}
                          </span>

                          {isOverridden && (
                            <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 bg-amber-100 text-amber-900 rounded border border-amber-300">
                              Human Override
                            </span>
                          )}
                        </div>

                        <select
                          value={currentSelected}
                          onChange={(e) => handleColumnSelect(fname, cField.key, e.target.value)}
                          className="w-full py-1.5 px-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono text-slate-800 font-semibold focus:outline-none focus:border-blue-500"
                        >
                          <option value="N/A">-- Unmapped / None --</option>
                          {sourceHeaders.map((srcH, hIdx) => (
                            <option key={hIdx} value={srcH}>
                              {srcH}
                            </option>
                          ))}
                        </select>

                        {mappedInfo && (
                          <div className="text-[10px] text-slate-500 flex items-center justify-between font-mono">
                            <span>AI Confidence: {mappedInfo.confidence ? Math.round(mappedInfo.confidence * 100) : 100}%</span>
                            <span className="truncate max-w-[180px]">{mappedInfo.rationale}</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-200">
        <button
          onClick={handleApplyOverridesAndReprocess}
          disabled={isReprocessing}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-2 transition disabled:opacity-50 cursor-pointer"
        >
          {isReprocessing ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Reprocessing Pipeline from Node 2...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Run From Node 2 (Apply Column Mapping Overrides)</span>
            </>
          )}
        </button>

        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2 transition cursor-pointer"
        >
          <span>Proceed to Step 4: Status Normalization</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
