import React from 'react';
import { UserCheck, ShieldAlert, Eye, CheckSquare } from 'lucide-react';

export default function HumanReviewGuideline({
  title = "Human Review Guidelines",
  role = "Finance Controller / Auditor Action",
  guidelines = [],
  actionHint
}) {
  return (
    <div className="mb-6 p-4 rounded-2xl bg-amber-50/80 border border-amber-200 text-amber-950 shadow-xs">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-xl bg-amber-100/90 text-amber-800 border border-amber-200 flex-shrink-0 mt-0.5">
          <UserCheck className="w-4 h-4" />
        </div>
        <div className="flex-1 space-y-1.5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h4 className="text-xs font-bold text-amber-950 flex items-center gap-1.5">
              <span>{title}</span>
              <span className="text-amber-500 font-normal">•</span>
              <span className="text-[11px] font-semibold text-amber-800">{role}</span>
            </h4>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
              Human-in-the-Loop
            </span>
          </div>

          <ul className="text-xs text-amber-900/90 space-y-1 font-medium leading-relaxed">
            {guidelines.map((item, idx) => (
              <li key={idx} className="flex items-start gap-1.5">
                <span className="text-amber-600 font-bold select-none">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>

          {actionHint && (
            <div className="pt-1.5 border-t border-amber-200/60 flex items-center gap-1.5 text-[11px] font-bold text-amber-800">
              <Eye className="w-3.5 h-3.5 text-amber-700 flex-shrink-0" />
              <span>{actionHint}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
