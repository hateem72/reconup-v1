import React, { useState } from 'react';
import { Upload, FileSpreadsheet, Clipboard, Play } from 'lucide-react';

export default function UploadSection({ onUploadSuccess, isProcessing }) {
  const [activeTab, setActiveTab] = useState('file');
  const [pasteData, setPasteData] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFileUpload = async (file) => {
    if (!file) return;
    setLoading(true);
    setErrorMsg('');
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/api/batches', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      onUploadSuccess(data);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePasteSubmit = async () => {
    if (!pasteData.trim()) return;
    setLoading(true);
    setErrorMsg('');
    try {
      const formData = new FormData();
      formData.append('raw_csv', pasteData.trim());

      const res = await fetch('/api/batches', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Paste processing failed');
      onUploadSuccess(data);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 mb-8 border border-slate-200 bg-white shadow-soft">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4 border-b border-slate-200 pb-3">
        <div>
          <h2 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-blue-600" />
            Step 1: Ingest E-Commerce Settlement & Order Files
          </h2>
          <p className="text-xs text-slate-500">Upload Meesho, Amazon, Flipkart, or Shopify payment sheets to initiate reconciliation</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('file')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${activeTab === 'file' ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
          >
            <Upload className="w-3.5 h-3.5 inline mr-1" />
            Upload Spreadsheet (.xlsx, .csv, .zip)
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${activeTab === 'paste' ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
          >
            <Clipboard className="w-3.5 h-3.5 inline mr-1" />
            Paste Clipboard CSV
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl">
          {errorMsg}
        </div>
      )}

      {activeTab === 'file' ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
              handleFileUpload(e.dataTransfer.files[0]);
            }
          }}
          className={`border-2 border-dashed rounded-2xl p-10 text-center transition cursor-pointer ${dragOver ? 'border-blue-600 bg-blue-50/50' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'}`}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".xlsx,.xls,.csv,.zip"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="w-10 h-10 text-blue-600 mx-auto mb-3" />
            <p className="text-sm font-extrabold text-slate-900">
              Drag & drop settlement spreadsheet or <span className="text-blue-600 underline">browse computer</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">Supports Meesho, Amazon, Flipkart, Shopify Excel/CSV or ZIP packages</p>
          </label>
        </div>
      ) : (
        <div>
          <textarea
            rows={5}
            value={pasteData}
            onChange={(e) => setPasteData(e.target.value)}
            placeholder="Paste tab-delimited Excel cells or CSV rows (e.g. SKU ID, Status, Amount)..."
            className="w-full p-3.5 rounded-xl bg-slate-50 border border-slate-300 text-xs text-slate-900 focus:outline-none focus:border-blue-600 font-mono"
          />
          <div className="mt-3 flex justify-end">
            <button
              onClick={handlePasteSubmit}
              disabled={loading || !pasteData.trim()}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center gap-2 disabled:opacity-50 shadow-md transition"
            >
              <Play className="w-3.5 h-3.5" />
              Process Pasted Data
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
