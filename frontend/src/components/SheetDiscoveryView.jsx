import React, { useState, useEffect } from 'react';
import { Filter, CheckCircle2, XCircle, FileSpreadsheet, Bot, ArrowRight, RefreshCw, ToggleLeft, ToggleRight, Play, Code } from 'lucide-react';
import RawJsonModal from './RawJsonModal';
import HumanReviewGuideline from './HumanReviewGuideline';

export default function SheetDiscoveryView({ batchId, onNext, onReprocessSuccess }) {
  const [nodeDetails, setNodeDetails] = useState(null);
  const [sheetOverrides, setSheetOverrides] = useState({});
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
          const initialOverrides = data.human_overrides?.sheet_overrides || {};
          setSheetOverrides(initialOverrides);
        }
      } catch (err) {
        console.error("Error fetching sub-tab details:", err);
      }
    };

    fetchDetails();
  }, [batchId]);

  const handleToggleSheet = (filename, currentVerdict) => {
    const activeState = sheetOverrides[filename] || (currentVerdict === 'REQUIRED' ? 'KEEP' : 'EXCLUDE');
    const newState = activeState === 'KEEP' ? 'EXCLUDE' : 'KEEP';
    setSheetOverrides(prev => ({
      ...prev,
      [filename]: newState
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
          start_node: 1.5,
          sheet_overrides: sheetOverrides
        })
      });
      if (res.ok) {
        if (onReprocessSuccess) onReprocessSuccess(batchId, 1.5);
      }
    } catch (err) {
      console.error("Error reprocessing from Node 1.5:", err);
    } finally {
      setIsReprocessing(false);
    }
  };

  if (!batchId) {
    return null;
  }

  const n15 = nodeDetails?.node1_5 || nodeDetails?.pipeline_store?.node1_5_result || nodeDetails || {};
  const retained = n15.retained_datasets || [];
  const dropped = n15.dropped_datasets || [];
  const allSheets = n15.all_sheets_evaluated || [...retained, ...dropped];

  return (
    <div className="rounded-3xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <RawJsonModal
        title="Node 1.5 Sheet Relevance Evaluation"
        data={n15}
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 border border-blue-200">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 2: Node 1.5 AI Sheet Relevance & Human Control</h2>
            <p className="text-xs text-slate-500 font-medium">
              Autonomous Agent <strong className="text-blue-700">SheetRelevanceAgent</strong> evaluates workbooks. Human operator can override any sub-tab state.
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
            Interactive Human Control Active
          </span>
        </div>
      </div>

      <HumanReviewGuideline
        title="Node 1.5 Sub-Tab Relevance Audit Guidelines"
        role="Sub-Tab Classification Review"
        guidelines={[
          "Confirm that all transaction sub-tabs containing order payouts are marked as 'REQUIRED (Retained)'.",
          "Verify that non-transactional disclaimer notes, summary tables, or empty sheets (0 rows) are marked as 'EXCLUDED (Dropped)'.",
          "If the AI incorrectly dropped an important settlement sub-tab, click the toggle button to KEEP it and re-process from Node 1.5."
        ]}
        actionHint="Adjust any sheet toggle and click 'Save Overrides & Re-Process from Node 1.5' to update the pipeline."
      />

      <div className="space-y-3">
        <h3 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider">
          Discovered Workbook Sub-Tabs ({allSheets.length}) — Toggle to Keep or Exclude:
        </h3>

        {allSheets.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs font-bold bg-slate-50 rounded-xl border border-slate-200">
            No sub-tabs discovered. Please upload files in Step 1.
          </div>
        ) : (
          allSheets.map((sheet, idx) => {
            const fname = sheet.filename;
            const isAiRetained = sheet.verdict === 'REQUIRED';
            const currentOverride = sheetOverrides[fname];
            const isKept = currentOverride ? currentOverride === 'KEEP' : isAiRetained;
            const isModified = currentOverride && ((isAiRetained && currentOverride === 'EXCLUDE') || (!isAiRetained && currentOverride === 'KEEP'));

            return (
              <div
                key={idx}
                className={`p-4 rounded-xl border transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                  isKept
                    ? 'bg-emerald-50/50 border-emerald-200'
                    : 'bg-rose-50/50 border-rose-200 opacity-75'
                }`}
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className={`w-4 h-4 ${isKept ? 'text-emerald-600' : 'text-rose-600'}`} />
                    <span className="text-xs font-extrabold text-slate-900">{fname}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-200 text-slate-800">
                      {sheet.role || 'SUB-TAB'}
                    </span>

                    {isModified && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-100 text-amber-900 border border-amber-300">
                        Human Override Active
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-600 font-medium">
                    AI Rationale: {sheet.rationale} ({sheet.row_count || 0} rows)
                  </p>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span className={`text-xs font-mono font-bold ${isKept ? 'text-emerald-700' : 'text-rose-700'}`}>
                    {isKept ? 'KEEP (INCLUDED)' : 'EXCLUDE (DROPPED)'}
                  </span>

                  <button
                    onClick={() => handleToggleSheet(fname, sheet.verdict)}
                    className="p-1 text-slate-700 hover:text-slate-900 transition cursor-pointer"
                    title={isKept ? "Switch to Exclude" : "Switch to Keep"}
                  >
                    {isKept ? (
                      <ToggleRight className="w-8 h-8 text-emerald-600" />
                    ) : (
                      <ToggleLeft className="w-8 h-8 text-slate-400" />
                    )}
                  </button>
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
              <span>Reprocessing Pipeline from Node 1.5...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-white" />
              <span>Run From Node 1.5 (Apply Sub-Tab Overrides)</span>
            </>
          )}
        </button>

        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2 transition cursor-pointer"
        >
          <span>Proceed to Step 3: LLM Mapping Matrix</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
