import React, { useState } from 'react';
import { Upload, FileSpreadsheet, FileText, CheckCircle2, ArrowRight, Shield, RefreshCw } from 'lucide-react';

export default function UploadSection({ onUploadSuccess, isProcessing }) {
  const [orderFile, setOrderFile] = useState(null);
  const [paymentFile, setPaymentFile] = useState(null);
  const [uploadError, setUploadError] = useState('');

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!orderFile && !paymentFile) {
      setUploadError('Please select at least one Order Manifest file or Payment Settlement workbook.');
      return;
    }

    setUploadError('');
    const formData = new FormData();

    if (orderFile) {
      formData.append('order_files', orderFile);
    }
    if (paymentFile) {
      formData.append('payment_files', paymentFile);
    }

    try {
      const res = await fetch('/api/batches', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        onUploadSuccess(data);
      } else {
        setUploadError(data.detail || 'Upload failed. Please check spreadsheet file formats.');
      }
    } catch (err) {
      setUploadError('Failed to connect to backend server at http://localhost:8000.');
    }
  };

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-6 border-b border-slate-200 pb-4">
        <div className="p-3 rounded-2xl bg-blue-50 text-blue-600 border border-blue-200">
          <Upload className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-base font-extrabold text-slate-900">Step 1: Multi-Sheet Financial Dataset Ingestion</h2>
          <p className="text-xs text-slate-500 font-medium">
            Upload your Master Order Manifest and Payment Settlement Workbooks (.xlsx, .csv, .zip)
          </p>
        </div>
      </div>

      {uploadError && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold">
          ⚠️ {uploadError}
        </div>
      )}

      <form onSubmit={handleUploadSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Master Order Manifest Uploader */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 hover:border-blue-400 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-extrabold text-slate-900 flex items-center gap-2">
                <FileSpreadsheet className="w-4 h-4 text-blue-600" />
                Master Order Sheet (Manifest)
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 border border-blue-200 font-bold">
                Anchor Manifest
              </span>
            </div>
            
            <p className="text-[11px] text-slate-500 mb-4 font-medium">
              Contains Order IDs, SKUs, Order Dates, Quantities & Order Action Statuses.
            </p>

            <label className="block w-full cursor-pointer">
              <input
                type="file"
                accept=".xlsx,.xls,.csv,.zip"
                onChange={(e) => setOrderFile(e.target.files[0])}
                className="hidden"
              />
              <div className="p-4 rounded-xl border border-dashed border-slate-300 hover:border-blue-500 bg-white text-center transition">
                {orderFile ? (
                  <div className="flex items-center justify-center gap-2 text-emerald-700 text-xs font-bold font-mono">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{orderFile.name}</span>
                  </div>
                ) : (
                  <span className="text-xs text-slate-500 font-medium">
                    Click to select Master Order Sheet (.xlsx / .csv)
                  </span>
                )}
              </div>
            </label>
          </div>

          {/* Payment Settlement Workbook Uploader */}
          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 hover:border-emerald-400 transition">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-extrabold text-slate-900 flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-600" />
                Payment Settlement Workbook
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200 font-bold">
                Multi-Subtab Settlement
              </span>
            </div>

            <p className="text-[11px] text-slate-500 mb-4 font-medium">
              Contains multi-event payout lines, settlement amounts, fees & adjustments.
            </p>

            <label className="block w-full cursor-pointer">
              <input
                type="file"
                accept=".xlsx,.xls,.csv,.zip"
                onChange={(e) => setPaymentFile(e.target.files[0])}
                className="hidden"
              />
              <div className="p-4 rounded-xl border border-dashed border-slate-300 hover:border-emerald-500 bg-white text-center transition">
                {paymentFile ? (
                  <div className="flex items-center justify-center gap-2 text-emerald-700 text-xs font-bold font-mono">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{paymentFile.name}</span>
                  </div>
                ) : (
                  <span className="text-xs text-slate-500 font-medium">
                    Click to select Payment Settlement Sheet (.xlsx / .csv)
                  </span>
                )}
              </div>
            </label>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-slate-200">
          <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
            <Shield className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Exact header profiling preserved without string mangling or silent row drops.</span>
          </div>

          <button
            type="submit"
            disabled={isProcessing}
            className="px-6 py-3 rounded-xl text-xs font-extrabold bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 flex items-center gap-2 transition disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Processing Pipeline...</span>
              </>
            ) : (
              <>
                <span>Ingest & Execute AI Agents</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
