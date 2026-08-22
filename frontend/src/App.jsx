import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AgentMonitorBar from './components/AgentMonitorBar';
import PipelineStepper from './components/PipelineStepper';
import TerminalConsole from './components/TerminalConsole';
import UploadSection from './components/UploadSection';
import SheetDiscoveryView from './components/SheetDiscoveryView';
import ColumnMappingView from './components/ColumnMappingView';
import ReconciliationView from './components/ReconciliationView';
import ExceptionsView from './components/ExceptionsView';
import FinanceQAChat from './components/FinanceQAChat';

export default function App() {
  const [activeBatchId, setActiveBatchId] = useState(null);
  const [reconciliation, setReconciliation] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(1);
  const [resetNotification, setResetNotification] = useState('');

  const fetchBatchData = async (batchId) => {
    try {
      const recRes = await fetch(`/api/batches/${batchId}/reconciliation`);
      if (recRes.ok) {
        const recData = await recRes.json();
        setReconciliation(recData);
      }

      const excRes = await fetch(`/api/batches/${batchId}/exceptions`);
      if (excRes.ok) {
        const excData = await excRes.json();
        setExceptions(excData.exceptions || []);
      }
    } catch (err) {
      console.error("Error fetching batch data:", err);
    }
  };

  const handleUploadSuccess = (data) => {
    setActiveBatchId(data.batch_id);
    fetchBatchData(data.batch_id);
    setPipelineStep(4); // Advance to Step 4: Order Reconciliation FIRST!
  };

  const handleHardReset = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch('/api/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setActiveBatchId(null);
        setReconciliation(null);
        setExceptions([]);
        setPipelineStep(1);
        setResetNotification('System Hard Reset complete! Database batches & agent state cleared.');
        setTimeout(() => setResetNotification(''), 4000);
      }
    } catch (err) {
      console.error("Error resetting system:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const runSyntheticDemo = async () => {
    setIsProcessing(true);
    try {
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
        setPipelineStep(4); // Advance to Step 4: Order Reconciliation FIRST!
      }
    } catch (err) {
      console.error("Error running synthetic demo:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        onRunDemo={runSyntheticDemo}
        onHardReset={handleHardReset}
        isProcessing={isProcessing}
        activeBatchId={activeBatchId}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {/* Reset Notification Banner */}
        {resetNotification && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold flex items-center justify-between shadow-xs">
            <span>{resetNotification}</span>
            <button onClick={() => setResetNotification('')} className="text-rose-600 hover:underline">
              Dismiss
            </button>
          </div>
        )}

        {/* Autonomous AI Agent Intelligence Fleet Monitor */}
        <AgentMonitorBar
          activeStep={pipelineStep}
          retainedSheetsCount={reconciliation ? 4 : 0}
          droppedSheetsCount={reconciliation ? 12 : 0}
        />

        {/* 6-Stage Interactive Workflow Stepper */}
        <PipelineStepper
          currentStep={pipelineStep}
          setStep={setPipelineStep}
          pendingExceptionsCount={exceptions.length}
        />

        {/* Real-time Streaming Agent Execution Console */}
        <TerminalConsole batchId={activeBatchId} isProcessing={isProcessing} />

        {/* STEP 1: MULTI-FILE INGESTION */}
        {pipelineStep === 1 && (
          <UploadSection onUploadSuccess={handleUploadSuccess} isProcessing={isProcessing} />
        )}

        {/* STEP 2: AI SHEET RELEVANCE & SUB-TAB FILTERING */}
        {pipelineStep === 2 && (
          <SheetDiscoveryView onNext={() => setPipelineStep(3)} />
        )}

        {/* STEP 3: LLM COLUMN MAPPING MATRIX */}
        {pipelineStep === 3 && (
          <ColumnMappingView onNext={() => setPipelineStep(4)} />
        )}

        {/* STEP 4: DETERMINISTIC 3-WAY ORDER RECONCILIATION */}
        {pipelineStep === 4 && (
          <ReconciliationView reconciliation={reconciliation} />
        )}

        {/* STEP 5: HUMAN-IN-THE-LOOP GOVERNANCE & EXCEPTIONS */}
        {pipelineStep === 5 && (
          <ExceptionsView
            exceptions={exceptions}
            batchId={activeBatchId}
            onExceptionResolved={() => fetchBatchData(activeBatchId)}
            onNext={() => setPipelineStep(6)}
          />
        )}

        {/* STEP 6: AI FINANCE CONTROLLER Q&A CONSOLE */}
        {pipelineStep === 6 && (
          <FinanceQAChat batchId={activeBatchId} />
        )}
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 bg-white font-medium">
        FINANCE CONTROLLER AI • Hackathon System • Powered by FastAPI, LangGraph & Local LLM (qwen2.5:3b)
      </footer>
    </div>
  );
}
