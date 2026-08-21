import React, { useEffect, useState } from 'react';
import { X, BookOpen } from 'lucide-react';

export default function RuleRegistryModal({ isOpen, onClose }) {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchRules();
    }
  }, [isOpen]);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/rules');
      const data = await res.json();
      setRules(data.rules || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-2xl p-6 border border-slate-200 rounded-2xl shadow-2xl bg-white">
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-extrabold text-slate-900">Learned Financial Rule Registry</h2>
              <p className="text-xs text-slate-500">Persisted marketplace deduction & status rules learned from human approvals</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 max-h-96 overflow-y-auto">
          {loading ? (
            <p className="text-xs text-slate-500 text-center py-8">Loading persisted database rules...</p>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 sticky top-0 uppercase tracking-wider text-[10px] font-bold">
                <tr>
                  <th className="p-2.5">Pattern</th>
                  <th className="p-2.5">Category</th>
                  <th className="p-2.5">Effect</th>
                  <th className="p-2.5">Source</th>
                  <th className="p-2.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {rules.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="p-2.5 font-mono font-bold text-blue-700">{r.pattern}</td>
                    <td className="p-2.5 text-slate-800">{r.normalized_category}</td>
                    <td className="p-2.5 font-bold text-rose-700">{r.financial_effect}</td>
                    <td className="p-2.5 text-slate-500 capitalize">{r.created_by}</td>
                    <td className="p-2.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Active
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
