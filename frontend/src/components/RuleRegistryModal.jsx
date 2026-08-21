import React, { useEffect, useState } from 'react';
import { X, BookOpen, ShieldCheck } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-2xl p-6 border border-gray-800 rounded-2xl shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-semibold text-white">Learned Financial Rule Registry</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 max-h-96 overflow-y-auto">
          {loading ? (
            <p className="text-xs text-gray-400 text-center py-8">Loading persisted database rules...</p>
          ) : (
            <table className="w-full text-left text-xs">
              <thead className="bg-gray-900 text-gray-400 sticky top-0 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="p-2.5">Pattern</th>
                  <th className="p-2.5">Category</th>
                  <th className="p-2.5">Effect</th>
                  <th className="p-2.5">Source</th>
                  <th className="p-2.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {rules.map((r) => (
                  <tr key={r.id} className="hover:bg-gray-800/40">
                    <td className="p-2.5 font-mono font-medium text-blue-400">{r.pattern}</td>
                    <td className="p-2.5 text-gray-200">{r.normalized_category}</td>
                    <td className="p-2.5 font-bold text-rose-400">{r.financial_effect}</td>
                    <td className="p-2.5 text-gray-400 capitalize">{r.created_by}</td>
                    <td className="p-2.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
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
