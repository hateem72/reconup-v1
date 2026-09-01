import React, { useState, useEffect } from 'react';
import { Database, FileSpreadsheet, Layers, Table, ArrowRight, RefreshCw, Code } from 'lucide-react';
import RawJsonModal from './RawJsonModal';
import HumanReviewGuideline from './HumanReviewGuideline';

export default function IngestInspectionView({ batchId, onNext }) {
  const [nodeDetails, setNodeDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showJsonModal, setShowJsonModal] = useState(false);

  useEffect(() => {
    if (!batchId) return;

    const fetchNodeDetails = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/batches/${batchId}/node-details`);
        if (res.ok) {
          const data = await res.json();
          setNodeDetails(data);
        }
      } catch (err) {
        console.error("Error fetching node 1 details:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchNodeDetails();
  }, [batchId]);

  if (!batchId) {
    return null;
  }

  const profiles = nodeDetails?.node1?.sheet_profiles || [];

  return (
    <div className="rounded-3xl bg-white border border-slate-200 p-6 shadow-sm space-y-5">
      <RawJsonModal
        title="Node 1 Ingest & Header Profiling"
        data={nodeDetails?.node1 || { sheet_profiles: [] }}
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
      />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-blue-50 text-blue-700 border border-blue-200">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 1: Node 1 Extracted Data & Header Profiling</h2>
            <p className="text-xs text-slate-500 font-medium">
              Exact source headers, dimensions, header row index, and statistical profiles extracted across uploaded workbooks
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

          <span className="px-3 py-1.5 rounded-full text-xs font-mono font-bold bg-blue-100 text-blue-800 border border-blue-300">
            {profiles.length} Discovered Sub-Tabs
          </span>
        </div>
      </div>

      <HumanReviewGuideline
        title="Node 1 Ingestion Audit Guidelines"
        role="File Integrity & Header Verification"
        guidelines={[
          "Verify that all uploaded Master Order manifest and Payment Settlement workbooks are listed below.",
          "Check that the total row counts and column dimensions match your physical source spreadsheets.",
          "Confirm that multi-tab workbooks (e.g. .xlsx with multiple sub-sheets) have all sub-tabs successfully profiled."
        ]}
        actionHint="If any file failed to parse or has corrupt headers, re-upload the spreadsheet before proceeding."
      />

      {loading ? (
        <div className="p-8 text-center text-slate-500 text-xs font-bold flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
          Loading Node 1 extracted profiling data...
        </div>
      ) : profiles.length === 0 ? (
        <div className="p-6 text-center text-slate-500 text-xs font-bold bg-slate-50 rounded-xl border border-slate-200">
          No workbook sheet profiles extracted yet. Please upload files above.
        </div>
      ) : (
        <div className="space-y-4">
          {profiles.map((prof, idx) => {
            const headers = prof.exact_headers || prof.column_profiles?.map(c => c.column_name) || [];
            const cleanHeaders = headers.filter(h => h !== 'id');

            return (
              <div key={idx} className="p-5 rounded-xl bg-slate-50/70 border border-slate-200 space-y-4">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="w-4 h-4 text-blue-600 shrink-0" />
                    <span className="text-xs font-extrabold text-slate-900">{prof.sheet_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-200 text-slate-800">
                      {prof.role || 'WORKBOOK SUB-TAB'}
                    </span>
                  </div>

                  <div className="flex items-center gap-3 text-[11px] font-mono text-slate-600 font-semibold">
                    <span>{prof.row_count} data rows</span>
                    <span>•</span>
                    <span>{cleanHeaders.length} columns</span>
                    <span>•</span>
                    <span>Header Row: {prof.header_row_index || 1}</span>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-bold text-slate-700 block mb-2">
                    Exact Discovered Header Column Names ({cleanHeaders.length}):
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {cleanHeaders.map((h, hIdx) => (
                      <span
                        key={hIdx}
                        className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-xs font-mono font-semibold text-slate-800 shadow-2xs"
                      >
                        [{hIdx + 1}] {h}
                      </span>
                    ))}
                  </div>
                </div>

                {prof.column_profiles && prof.column_profiles.length > 0 && (
                  <div>
                    <span className="text-[11px] font-bold text-slate-700 block mb-2">
                      Column Statistical Profiles & Preview Samples:
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono">
                      {prof.column_profiles.filter(c => c.column_name !== 'id').slice(0, 6).map((cp, cIdx) => (
                        <div key={cIdx} className="p-2.5 rounded-lg bg-white border border-slate-200 space-y-1">
                          <div className="flex items-center justify-between font-bold text-slate-800">
                            <span>{cp.column_name}</span>
                            <span className="text-[10px] text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
                              {cp.numeric_like ? 'NUMERIC' : cp.identifier_like ? 'IDENTIFIER' : cp.date_like ? 'DATE' : 'TEXT'}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-500 flex justify-between">
                            <span>Nulls: {cp.null_percentage}%</span>
                            <span>Uniqueness: {Math.round(cp.uniqueness_ratio * 100)}%</span>
                          </div>
                          {cp.sample_values && cp.sample_values.length > 0 && (
                            <div className="text-[10px] text-slate-600 truncate">
                              Samples: {cp.sample_values.slice(0, 3).join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="flex justify-end pt-4 border-t border-slate-200">
        <button
          onClick={onNext}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2 transition cursor-pointer"
        >
          <span>Proceed to Step 2: AI Sub-Tab Filter & Human Control</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
