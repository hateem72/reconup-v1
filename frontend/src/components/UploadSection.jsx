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
    <div className="glass-panel p-6 mb-8 border border-gray-800">
      <div className="flex items-center justify-between mb-4 border-b border-gray-800 pb-3">
        <h2 className="text-base font-semibold text-white flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-blue-400" />
          Ingest E-Commerce Settlement & Order Manifests
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('file')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${activeTab === 'file' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}`}
          >
            <Upload className="w-3.5 h-3.5 inline mr-1" />
            Upload File (.xlsx, .csv, .zip)
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${activeTab === 'paste' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-white'}`}
          >
            <Clipboard className="w-3.5 h-3.5 inline mr-1" />
            Paste Clipboard CSV
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl">
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
          className={`border-2 border-dashed rounded-xl p-8 text-center transition cursor-pointer ${dragOver ? 'border-blue-500 bg-blue-500/5' : 'border-gray-800 hover:border-gray-700 bg-gray-900/40'}`}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".xlsx,.xls,.csv,.zip"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="w-10 h-10 text-gray-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-200">
              Drag & drop settlement spreadsheets or <span className="text-blue-400 underline">browse</span>
            </p>
            <p className="text-xs text-gray-500 mt-1">Supports Meesho, Amazon, Flipkart, Shopify Excel/CSV or ZIP packages</p>
          </label>
        </div>
      ) : (
        <div>
          <textarea
            rows={4}
            value={pasteData}
            onChange={(e) => setPasteData(e.target.value)}
            placeholder="Paste tab-delimited Excel cells or CSV data (e.g. SKU ID, Status, Amount)..."
            className="w-full p-3 rounded-xl bg-gray-900 border border-gray-800 text-xs text-gray-200 focus:outline-none focus:border-blue-500 font-mono"
          />
          <div className="mt-3 flex justify-end">
            <button
              onClick={handlePasteSubmit}
              disabled={loading || !pasteData.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold flex items-center gap-2 disabled:opacity-50"
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
