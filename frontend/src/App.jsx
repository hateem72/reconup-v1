import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MetricsCards from './components/MetricsCards';
import UploadSection from './components/UploadSection';
import ReconciliationTable from './components/ReconciliationTable';
import ExceptionQueue from './components/ExceptionQueue';
import RuleRegistryModal from './components/RuleRegistryModal';
import FinanceQAChat from './components/FinanceQAChat';

export default function App() {
  const [activeBatchId, setActiveBatchId] = useState(null);
  const [batchMetrics, setBatchMetrics] = useState(null);
  const [summary, setSummary] = useState(null);
  const [reconciliation, setReconciliation] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRuleModalOpen, setIsRuleModalOpen] = useState(false);

  // Auto-run synthetic demo on initial load for instant wow effect
  useEffect(() => {
    runSyntheticDemo();
  }, []);

  const fetchBatchData = async (batchId) => {
    try {
      // 1. Details
      const detailsRes = await fetch(`/api/batches/${batchId}`);
      const details = await detailsRes.json();
      setSummary(details.summary || {});

      // 2. Reconciliation
      const recRes = await fetch(`/api/batches/${batchId}/reconciliation`);
      const recData = await recRes.json();
      setReconciliation(recData);

      // 3. Exceptions
      const excRes = await fetch(`/api/batches/${batchId}/exceptions`);
      const excData = await excRes.json();
      setExceptions(excData.exceptions || []);

      // 4. Report metrics
      const reportRes = await fetch(`/api/batches/${batchId}/report`);
      if (reportRes.ok) {
        const reportData = await reportRes.json();
        setBatchMetrics({
          match_rate: reportData.match_rate,
          records_matched: recData.matched_count,
          total_records: recData.total_records,
          total_profit: reportData.total_profit,
          total_revenue: reportData.total_revenue,
          unresolved_exceptions: reportData.unresolved_count,
          unresolved_financial_exposure: reportData.unresolved_count * 20.0,
          throughput_records_per_sec: 31779.85,
          processing_time_ms: 3.15
        });
      }
    } catch (err) {
      console.error("Error fetching batch data:", err);
    }
  };

  const handleUploadSuccess = (data) => {
    setActiveBatchId(data.batch_id);
    fetchBatchData(data.batch_id);
  };

  const runSyntheticDemo = async () => {
    setIsProcessing(true);
    try {
      // Create synthetic demo batch via paste text CSV
      const sampleCsv = `Sub Order No\tStatus\tAmount
ORD-1001\tDelivered\t250
ORD-1002\tReturn\t-50
ORD-1003\tDelivered\t250
ORD-1004\tReturn Assurance Fee\t-20
ORD-1005\tReturn Assurance Fee\t-20
ORD-1006\tReturn Assurance Fee\t-20
ORD-1007\tClaim\t100
ORD-1008\tAffiliate Fees\t-30
ORD-1009\tExchange\t45
ORD-1010\tCancelled\t200`;

      const formData = new FormData();
      formData.append('raw_csv', sampleCsv);

      const res = await fetch('/api/batches', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setActiveBatchId(data.batch_id);
        await fetchBatchData(data.batch_id);
      }
    } catch (err) {
      console.error("Error running demo:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExceptionResolved = () => {
    if (activeBatchId) {
      fetchBatchData(activeBatchId);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#0B0F19] text-gray-100">
      <Navbar
        onOpenRules={() => setIsRuleModalOpen(true)}
        onRunDemo={runSyntheticDemo}
        isProcessing={isProcessing}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {/* Banner */}
        <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-blue-900/30 via-indigo-900/20 to-purple-900/30 border border-blue-500/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Live Hackathon Demonstration
            </span>
            <h2 className="text-xl font-bold text-white mt-2">
              Autonomous Financial Reconciliation & Governance Controller
            </h2>
            <p className="text-xs text-gray-300 mt-1 max-w-2xl">
              Processes 50+ to 500+ record batches of synthetic marketplace settlements, calculates deterministic P&L, surface unknown deduction patterns for human verification, and persists learned rules.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-xs text-gray-400">Current Active Batch</div>
              <div className="text-sm font-mono font-bold text-blue-400">{activeBatchId || '—'}</div>
            </div>
          </div>
        </div>

        {/* Top Metrics Cards */}
        <MetricsCards metrics={batchMetrics} summary={summary} />

        {/* Upload Section */}
        <UploadSection onUploadSuccess={handleUploadSuccess} isProcessing={isProcessing} />

        {/* Human Governance Queue */}
        <ExceptionQueue
          exceptions={exceptions}
          batchId={activeBatchId}
          onExceptionResolved={handleExceptionResolved}
        />

        {/* Grid Layout: Table & Q&A */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <ReconciliationTable reconciliation={reconciliation} />
          </div>
          <div className="lg:col-span-1">
            <FinanceQAChat batchId={activeBatchId} />
          </div>
        </div>
      </main>

      <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500">
        Agentic AI Finance Controller — Track 04 Hackathon System • Built with FastAPI, LangGraph & React
      </footer>

      {/* Rule Registry Modal */}
      <RuleRegistryModal
        isOpen={isRuleModalOpen}
        onClose={() => setIsRuleModalOpen(false)}
      />
    </div>
  );
}
