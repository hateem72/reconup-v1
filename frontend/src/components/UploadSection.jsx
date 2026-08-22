import React, { useState } from 'react';
import { Upload, FileSpreadsheet, Clipboard, Play, X, FileCheck } from 'lucide-react';

export default function UploadSection({ onUploadSuccess, isProcessing }) {
  const [activeTab, setActiveTab] = useState('file');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [pasteData, setPasteData] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFileSelect = (newFiles) => {
    const fileArray = Array.from(newFiles);
    setSelectedFiles(prev => {
      const existingNames = new Set(prev.map(f => f.name));
      const filtered = fileArray.filter(f => !existingNames.has(f.name));
      return [...prev, ...filtered];
    });
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleMultiFileUpload = async () => {
    if (selectedFiles.length === 0) return;
    setLoading(true);
    setErrorMsg('');
    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      const res = await fetch('/api/batches', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      onUploadSuccess(data);
      setSelectedFiles([]);
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
            Step 1: Ingest Order & Multi-Source Payment Settlement Files
          </h2>
          <p className="text-xs text-slate-500">Upload your Order Sheet + multiple Payment Settlement files (Excel, CSV, ZIP) to run reconciliation</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('file')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${activeTab === 'file' ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
          >
            <Upload className="w-3.5 h-3.5 inline mr-1" />
            Multiple File Upload (.xlsx, .csv, .zip)
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
        <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl font-medium">
          {errorMsg}
        </div>
      )}

      {activeTab === 'file' ? (
        <div className="space-y-4">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                handleFileSelect(e.dataTransfer.files);
              }
            }}
            className={`border-2 border-dashed rounded-2xl p-8 text-center transition cursor-pointer ${dragOver ? 'border-blue-600 bg-blue-50/50' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'}`}
          >
            <input
              type="file"
              id="file-upload-multi"
              className="hidden"
              multiple
              accept=".xlsx,.xls,.csv,.zip"
              onChange={(e) => e.target.files && handleFileSelect(e.target.files)}
            />
            <label htmlFor="file-upload-multi" className="cursor-pointer">
              <Upload className="w-10 h-10 text-blue-600 mx-auto mb-2" />
              <p className="text-sm font-extrabold text-slate-900">
                Drag & drop Order Sheet + Payment Files or <span className="text-blue-600 underline">browse files</span>
              </p>
              <p className="text-xs text-slate-500 mt-1">Select multiple files at once (e.g. Orders July + June Payments + July Payments)</p>
            </label>
          </div>

          {/* Selected Files Badge List */}
          {selectedFiles.length > 0 && (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <FileCheck className="w-4 h-4 text-emerald-600" />
                  Selected Files ({selectedFiles.length}):
                </span>
                <button
                  onClick={() => setSelectedFiles([])}
                  className="text-[11px] text-rose-600 hover:underline font-bold"
                >
                  Clear All
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedFiles.map((file, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-slate-300 text-xs font-mono font-bold text-slate-800 shadow-xs">
                    <span className="truncate max-w-xs">{file.name}</span>
                    <span className="text-[10px] text-slate-400 font-sans">({(file.size / 1024).toFixed(1)} KB)</span>
                    <button onClick={() => removeFile(idx)} className="text-slate-400 hover:text-rose-600 ml-1">
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleMultiFileUpload}
                  disabled={loading || selectedFiles.length === 0}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center gap-2 shadow-md disabled:opacity-50 transition"
                >
                  <Play className="w-3.5 h-3.5" />
                  {loading ? 'Processing Files...' : `Process ${selectedFiles.length} Uploaded Files`}
                </button>
              </div>
            </div>
          )}
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
