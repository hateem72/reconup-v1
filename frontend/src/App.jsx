import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import AgentMonitorBar from './components/AgentMonitorBar';
import PipelineStepper from './components/PipelineStepper';
import TerminalConsole from './components/TerminalConsole';
import UploadSection from './components/UploadSection';
import IngestInspectionView from './components/IngestInspectionView';
import SheetDiscoveryView from './components/SheetDiscoveryView';
import ColumnMappingView from './components/ColumnMappingView';
import StatusNormalizationView from './components/StatusNormalizationView';
import StatusIntegrityView from './components/StatusIntegrityView';
import ReconciliationView from './components/ReconciliationView';
import ExceptionsView from './components/ExceptionsView';
import FinanceQAChat from './components/FinanceQAChat';
import ReportSummaryView from './components/ReportSummaryView';

export default function App() {
  const [activeBatchId, setActiveBatchId] = useState(null);
  const [reconciliation, setReconciliation] = useState(null);
  const [exceptions, setExceptions] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(1);
  const [resetNotification, setResetNotification] = useState('');
  
  // Real-time Node Execution State (SSE) across 8 Node Steps
  const [nodeStates, setNodeStates] = useState({
    1: 'pending',
    2: 'pending',
    3: 'pending',
    4: 'pending',
    5: 'pending',
    6: 'pending',
    7: 'pending',
    8: 'pending'
  });
  const [activeNodeMessage, setActiveNodeMessage] = useState('');
  const eventSourceRef = useRef(null);

  const fetchBatchData = async (batchId) => {
    if (!batchId) return;
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

  const startEventStream = (batchId, initialStartNode = 1) => {
    if (!batchId) return;

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsProcessing(true);
    
    // Set initial node states
    setNodeStates(prev => {
      const updated = { ...prev };
      for (let i = 1; i <= 8; i++) {
        if (i < initialStartNode) {
          updated[i] = 'completed';
        } else if (i === initialStartNode) {
          updated[i] = 'running';
        } else {
          updated[i] = 'pending';
        }
      }
      return updated;
    });

    const es = new EventSource(`/api/batches/${batchId}/stream`);
    eventSourceRef.current = es;

    es.addEventListener('NODE_START', (event) => {
      try {
        const data = JSON.parse(event.data);
        const nodeNum = data.node;
        setNodeStates(prev => ({
          ...prev,
          [nodeNum]: 'running'
        }));
        setActiveNodeMessage(data.message || data.name || '');
      } catch (e) {
        console.error("Error in NODE_START handler:", e);
      }
    });

    es.addEventListener('NODE_COMPLETE', (event) => {
      try {
        const data = JSON.parse(event.data);
        const nodeNum = data.node;
        setNodeStates(prev => ({
          ...prev,
          [nodeNum]: 'completed'
        }));
      } catch (e) {
        console.error("Error in NODE_COMPLETE handler:", e);
      }
    });

    es.addEventListener('PIPELINE_COMPLETE', async (event) => {
      try {
        setNodeStates({
          1: 'completed',
          2: 'completed',
          3: 'completed',
          4: 'completed',
          5: 'completed',
          6: 'completed',
          7: 'completed',
          8: 'completed'
        });
        setActiveNodeMessage('');
        setIsProcessing(false);
        await fetchBatchData(batchId);
        setPipelineStep(6); // Auto-advance to Order Reconciliation upon pipeline completion
        es.close();
      } catch (e) {
        console.error("Error in PIPELINE_COMPLETE handler:", e);
      }
    });

    es.addEventListener('PIPELINE_ERROR', (event) => {
      try {
        const data = JSON.parse(event.data);
        setIsProcessing(false);
        setActiveNodeMessage(`Error: ${data.error || 'Execution stopped'}`);
        es.close();
      } catch (e) {
        console.error("Error in PIPELINE_ERROR handler:", e);
      }
    });

    es.onerror = () => {
      setIsProcessing(false);
    };
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleUploadStart = () => {
    setIsProcessing(true);
    setNodeStates({
      1: 'running',
      2: 'pending',
      3: 'pending',
      4: 'pending',
      5: 'pending',
      6: 'pending',
      7: 'pending',
      8: 'pending'
    });
    setActiveNodeMessage('Ingesting & parsing workbook sub-tabs...');
  };

  const handleUploadSuccess = (data) => {
    setActiveBatchId(data.batch_id);
    startEventStream(data.batch_id, 1);
  };

  const mapStartNodeToStepIndex = (startNode) => {
    if (!startNode) return 2;
    const num = parseFloat(startNode);
    if (num === 1.5) return 2; // Node 1.5 (Sub-Tab Filter) = Step 2
    if (num === 2.0 || num === 2) return 3; // Node 2 (Column Mapping) = Step 3
    if (num === 3.0 || num === 3) return 4; // Node 3 (Status Normalization) = Step 4
    if (num === 4.0 || num === 4) return 5; // Node 4 (Integrity Audit) = Step 5
    if (num === 5.0 || num === 5) return 6; // Node 5 (Order Reconciliation) = Step 6
    return 2;
  };

  const handleReprocessSuccess = (data) => {
    const bId = data.batch_id || activeBatchId;
    const stepIndex = mapStartNodeToStepIndex(data.start_node || 1.5);
    startEventStream(bId, stepIndex);
  };

  const handleHardReset = async () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsProcessing(true);
    try {
      const res = await fetch('/api/reset', { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        setActiveBatchId(null);
        setReconciliation(null);
        setExceptions([]);
        setPipelineStep(1);
        setNodeStates({ 1: 'pending', 2: 'pending', 3: 'pending', 4: 'pending', 5: 'pending', 6: 'pending', 7: 'pending', 8: 'pending' });
        setActiveNodeMessage('');
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
    setNodeStates({
      1: 'running',
      2: 'pending',
      3: 'pending',
      4: 'pending',
      5: 'pending',
      6: 'pending',
      7: 'pending',
      8: 'pending'
    });
    setActiveNodeMessage('Ingesting sample CSV data...');

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
        startEventStream(data.batch_id, 1);
      }
    } catch (err) {
      console.error("Error running synthetic demo:", err);
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
            <button onClick={() => setResetNotification('')} className="text-rose-600 hover:underline cursor-pointer">
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

        {/* 8-Stage Interactive Workflow Stepper with Real-Time SSE Status */}
        <PipelineStepper
          currentStep={pipelineStep}
          setStep={setPipelineStep}
          pendingExceptionsCount={exceptions.length}
          nodeStates={nodeStates}
          activeNodeMessage={activeNodeMessage}
        />

        {/* Real-time Streaming Agent Execution Console (SSE) */}
        <TerminalConsole batchId={activeBatchId} isProcessing={isProcessing} />

        {/* NODE 1: MULTI-FILE INGESTION & DATA PROFILING INSPECTION */}
        {pipelineStep === 1 && (
          <div className="space-y-6">
            <UploadSection 
              onUploadSuccess={handleUploadSuccess} 
              onUploadStart={handleUploadStart}
              isProcessing={isProcessing} 
            />
            {activeBatchId && (
              <IngestInspectionView batchId={activeBatchId} onNext={() => setPipelineStep(2)} />
            )}
          </div>
        )}

        {/* NODE 1.5: AI SHEET RELEVANCE & SUB-TAB FILTERING */}
        {pipelineStep === 2 && (
          <SheetDiscoveryView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(3)}
            onReprocessSuccess={handleReprocessSuccess}
          />
        )}

        {/* NODE 2: LLM COLUMN MAPPING MATRIX */}
        {pipelineStep === 3 && (
          <ColumnMappingView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(4)}
            onReprocessSuccess={handleReprocessSuccess}
          />
        )}

        {/* NODE 3: STATUS NORMALIZATION */}
        {pipelineStep === 4 && (
          <StatusNormalizationView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(5)}
            onReprocessSuccess={handleReprocessSuccess}
          />
        )}

        {/* NODE 4: STATUS INTEGRITY & FEE DEDUCTION AUDIT */}
        {pipelineStep === 5 && (
          <StatusIntegrityView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(6)}
          />
        )}

        {/* NODE 5: DETERMINISTIC ORDER RECONCILIATION */}
        {pipelineStep === 6 && (
          <ReconciliationView reconciliation={reconciliation} />
        )}

        {/* NODE 6: AI GOVERNANCE QUEUE & FINANCE Q&A CONSOLE */}
        {pipelineStep === 7 && (
          <div className="space-y-6">
            <ExceptionsView
              exceptions={exceptions}
              batchId={activeBatchId}
              onExceptionResolved={() => fetchBatchData(activeBatchId)}
              onNext={() => setPipelineStep(8)}
            />
            <FinanceQAChat batchId={activeBatchId} />
          </div>
        )}

        {/* NODE 7: EXECUTIVE AUDITED REPORT & EXPORT KPIS */}
        {pipelineStep === 8 && (
          <ReportSummaryView
            batchId={activeBatchId}
            reconciliation={reconciliation}
          />
        )}
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 bg-white font-medium">
        ReconUp • Autonomous AI Settlement Reconciliation System • Powered by FastAPI, LangGraph & Local LLM (qwen2.5:3b)
      </footer>
    </div>
  );
}
