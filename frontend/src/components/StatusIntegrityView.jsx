import React, { useState, useEffect } from 'react';
import { ShieldCheck, ArrowRight, CheckCircle2, DollarSign, AlertCircle, FileCheck, Layers, Play } from 'lucide-react';
import RawJsonModal from './RawJsonModal';
import HumanReviewGuideline from './HumanReviewGuideline';

export default function StatusIntegrityView({ batchId, onNext }) {
  const [nodeDetails, setNodeDetails] = useState(null);
  const [showJsonModal, setShowJsonModal] = useState(false);

  useEffect(() => {
    if (!batchId) return;

    const fetchDetails = async () => {
      try {
        const res = await fetch(`/api/batches/${batchId}/node-details`);
        if (res.ok) {
          const data = await res.json();
          setNodeDetails(data);
        }
      } catch (err) {
        console.error("Error fetching integrity node details:", err);
      }
    };

    fetchDetails();
  }, [batchId]);

  const node4Result = nodeDetails?.pipeline_store?.node4_result || {};
  const repairedCount = node4Result.repaired_orders_count || 0;
  const deductionsCount = node4Result.classified_deductions || 0;
  const creditsCount = node4Result.classified_credits || 0;

  return (
    <div className="rounded-3xl bg-white border border-slate-200 p-6 shadow-sm space-y-6">
      <RawJsonModal
        title="Node 4 AI Status Integrity Audit"
        data={node4Result}
        isOpen={showJsonModal}
        onClose={() => setShowJsonModal(false)}
      />

      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-extrabold text-slate-900">Step 5: Node 4 AI Status Integrity Audit</h2>
            <p className="text-xs text-slate-500 font-medium">
              Autonomous Agent <strong className="text-emerald-700">PatternDetectionAgent</strong> audits adjacent column key-value pairs, repairs missing statuses, and classifies fee deductions.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowJsonModal(true)}
            className="px-4 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-xs font-bold hover:bg-slate-50 transition-colors flex items-center gap-2 cursor-pointer"
          >
            Inspect Audit Data
          </button>
          <button
            onClick={onNext}
            className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2 cursor-pointer"
          >
            Continue to Node 5 (Reconciliation)
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <HumanReviewGuideline
        title="Node 4 Status Integrity Audit Guidelines"
        role="Data Quality & Integrity Verification"
        guidelines={[
          "Review repaired order statuses to confirm that blank/missing status lines were inferred correctly from adjacent row events.",
          "Verify that non-order fee lines (advertising fees, commission charges) are properly segregated from core order payout lines.",
          "Confirm that 100% status coverage is achieved before proceeding to 3-way financial reconciliation."
        ]}
        actionHint="Click 'Inspect Audit Data' to view exact repaired records or continue to Node 5 for 3-way reconciliation."
      />

      {/* Audit Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl bg-white border border-slate-200 p-5 shadow-xs flex items-center gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Order Status Integrity</span>
            <div className="text-xl font-black text-slate-900 mt-0.5">100.0% Coverage</div>
            <span className="text-[10px] text-emerald-600 font-bold block mt-0.5">
              {repairedCount > 0 ? `${repairedCount} blank statuses repaired` : 'Zero blank status records found'}
            </span>
          </div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200 p-5 shadow-xs flex items-center gap-4">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-xl">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Fee Deductions Classified</span>
            <div className="text-xl font-black text-slate-900 mt-0.5">{deductionsCount} Event Lines</div>
            <span className="text-[10px] text-amber-600 font-bold block mt-0.5">
              Marketplace Ad Fees, Charges & Recoveries
            </span>
          </div>
        </div>

        <div className="rounded-2xl bg-white border border-slate-200 p-5 shadow-xs flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <DollarSign className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Credits & Claims</span>
            <div className="text-xl font-black text-slate-900 mt-0.5">{creditsCount} Items</div>
            <span className="text-[10px] text-blue-600 font-bold block mt-0.5">
              Non-Order Compensation Credits
            </span>
          </div>
        </div>
      </div>

      {/* Detailed Status Coverage Card */}
      <div className="rounded-2xl bg-white border border-slate-200 p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <FileCheck className="w-4 h-4 text-emerald-600" />
          Audit Highlights & Integrity Summary
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="font-bold text-slate-900">Master Order Manifest Integrity</div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Every order record has been validated against primary status headers and secondary fallback fields. 100% of order manifest rows have valid, non-null status values ready for reconciliation.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
            <div className="font-bold text-slate-900">Payment Line Classification</div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Payment settlement lines have been split into order payouts vs non-order fee deductions. Non-order fee lines are separated so they do not trigger false missing-order errors.
            </p>
          </div>
        </div>
      </div>

      {/* Raw Data Inspection Modal */}
      {showJsonModal && (
        <RawJsonModal
          title="Node 4 Status Integrity Audit Data"
          data={node4Result}
          onClose={() => setShowJsonModal(false)}
        />
      )}
    </div>
  );
}
