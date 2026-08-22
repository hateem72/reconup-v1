import React, { useState } from 'react';
import { Upload, FileSpreadsheet, Clipboard, Play, X, FileCheck, Layers, Package, CreditCard } from 'lucide-react';

export default function UploadSection({ onUploadSuccess, isProcessing }) {
  const [activeTab, setActiveTab] = useState('file');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [pasteData, setPasteData] = useState('');
  const [dragOverOrder, setDragOverOrder] = useState(false);
  const [dragOverPayment, setDragOverPayment] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const addFilesWithRole = (newFiles, defaultRole = 'ORDER') => {
    const fileArray = Array.from(newFiles);
    setSelectedFiles(prev => {
      const existingNames = new Set(prev.map(f => f.file.name));
      const filtered = fileArray
        .filter(f => !existingNames.has(f.name))
        .map(f => {
          // Auto-detect payment role if filename contains payment keywords
          const fnameLower = f.name.toLowerCase();
          const autoRole = (fnameLower.includes('payment') || fnameLower.includes('settlement') || fnameLower.includes('payout')) ? 'PAYMENT' : defaultRole;
          return { file: f, role: autoRole };
        });
      return [...prev, ...filtered];
    });
  };

  const toggleFileRole = (index) => {
    setSelectedFiles(prev => prev.map((item, i) => {
      if (i === index) {
        return { ...item, role: item.role === 'ORDER' ? 'PAYMENT' : 'ORDER' };
      }
      return item;
    }));
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
      const rolesMap = {};

      selectedFiles.forEach(item => {
        rolesMap[item.file.name] = item.role;
        if (item.role === 'ORDER') {
          formData.append('order_files', item.file);
        } else {
          formData.append('payment_files', item.file);
        }
      });

      formData.append('file_roles_json', JSON.stringify(rolesMap));

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
            Step 1: Ingest Master Order Sheets & Payment Settlement Files
          </h2>
          <p className="text-xs text-slate-500">Designate Order Sheets vs Payment Settlement Sheets to profile and reconcile</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('file')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${activeTab === 'file' ? 'bg-blue-600 text-white shadow-sm' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
          >
            <Upload className="w-3.5 h-3.5 inline mr-1" />
            Upload Spreadsheets (.xlsx, .csv, .zip)
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Master Order Sheet Dropzone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOverOrder(true); }}
              onDragLeave={() => setDragOverOrder(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOverOrder(false);
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                  addFilesWithRole(e.dataTransfer.files, 'ORDER');
                }
              }}
              className={`border-2 border-dashed rounded-2xl p-6 text-center transition cursor-pointer ${dragOverOrder ? 'border-blue-600 bg-blue-50/50' : 'border-blue-200 hover:border-blue-400 bg-blue-50/20'}`}
            >
              <input
                type="file"
                id="file-upload-order"
                className="hidden"
                multiple
                accept=".xlsx,.xls,.csv,.zip"
                onChange={(e) => e.target.files && addFilesWithRole(e.target.files, 'ORDER')}
              />
              <label htmlFor="file-upload-order" className="cursor-pointer">
                <Package className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <p className="text-xs font-extrabold text-slate-900">
                  Upload <span className="text-blue-600">Master Order Sheet(s)</span>
                </p>
                <p className="text-[11px] text-slate-500 mt-1">Select Order CSV/XLSX file(s)</p>
              </label>
            </div>

            {/* Payment Settlement Sheet Dropzone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOverPayment(true); }}
              onDragLeave={() => setDragOverPayment(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOverPayment(false);
                if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                  addFilesWithRole(e.dataTransfer.files, 'PAYMENT');
                }
              }}
              className={`border-2 border-dashed rounded-2xl p-6 text-center transition cursor-pointer ${dragOverPayment ? 'border-emerald-600 bg-emerald-50/50' : 'border-emerald-200 hover:border-emerald-400 bg-emerald-50/20'}`}
            >
              <input
                type="file"
                id="file-upload-payment"
                className="hidden"
                multiple
                accept=".xlsx,.xls,.csv,.zip"
                onChange={(e) => e.target.files && addFilesWithRole(e.target.files, 'PAYMENT')}
              />
              <label htmlFor="file-upload-payment" className="cursor-pointer">
                <CreditCard className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
                <p className="text-xs font-extrabold text-slate-900">
                  Upload <span className="text-emerald-600">Payment Settlement Sheet(s)</span>
                </p>
                <p className="text-[11px] text-slate-500 mt-1">Select Payment CSV/XLSX/ZIP file(s)</p>
              </label>
            </div>
          </div>

          {/* Selected Files Badge List with Role Selector Toggle */}
          {selectedFiles.length > 0 && (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <FileCheck className="w-4 h-4 text-emerald-600" />
                  Selected Upload Manifest ({selectedFiles.length} files):
                </span>
                <button
                  onClick={() => setSelectedFiles([])}
                  className="text-[11px] text-rose-600 hover:underline font-bold"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-2">
                {selectedFiles.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-slate-200 text-xs shadow-xs">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="font-mono font-bold text-slate-900 truncate">{item.file.name}</span>
                      <span className="text-[10px] text-slate-400 font-sans">({(item.file.size / 1024).toFixed(1)} KB)</span>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => toggleFileRole(idx)}
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-extrabold transition flex items-center gap-1 ${
                          item.role === 'ORDER'
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                        title="Click to toggle file role between Order Sheet and Payment Settlement Sheet"
                      >
                        {item.role === 'ORDER' ? <Package className="w-3 h-3 text-blue-600" /> : <CreditCard className="w-3 h-3 text-emerald-600" />}
                        Role: {item.role === 'ORDER' ? 'Master Order Sheet' : 'Payment Settlement'}
                      </button>

                      <button onClick={() => removeFile(idx)} className="text-slate-400 hover:text-rose-600 p-1">
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
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
                  {loading ? 'Processing Node 1...' : `Run Node 1 & Process ${selectedFiles.length} Uploaded Files`}
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
