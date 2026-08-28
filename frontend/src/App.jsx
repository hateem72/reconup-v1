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
  
  // Real-time Node Execution State (SSE)
  const [nodeStates, setNodeStates] = useState({
    1: 'pending',
    2: 'pending',
    3: 'pending',
    4: 'pending',
    5: 'pending',
    6: 'pending'
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
      for (let i = 1; i <= 6; i++) {
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
          6: 'completed'
        });
        setActiveNodeMessage('');
        setIsProcessing(false);
        await fetchBatchData(batchId);
        setPipelineStep(5); // Auto-advance to Order Reconciliation upon pipeline completion
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
      // Stream closed or completed
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
      6: 'pending'
    });
    setActiveNodeMessage('Ingesting & parsing workbook sub-tabs...');
  };

  const handleUploadSuccess = (data) => {
    setActiveBatchId(data.batch_id);
    startEventStream(data.batch_id, 1);
  };

  const handleReprocessSuccess = (data) => {
    const bId = data.batch_id || activeBatchId;
    const sNode = data.start_node ? Math.floor(data.start_node) : 2;
    startEventStream(bId, sNode);
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
        setNodeStates({ 1: 'pending', 2: 'pending', 3: 'pending', 4: 'pending', 5: 'pending', 6: 'pending' });
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
      6: 'pending'
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

        {/* 6-Stage Interactive Workflow Stepper with Real-Time SSE Status */}
        <PipelineStepper
          currentStep={pipelineStep}
          setStep={setPipelineStep}
          pendingExceptionsCount={exceptions.length}
          nodeStates={nodeStates}
          activeNodeMessage={activeNodeMessage}
        />

        {/* Real-time Streaming Agent Execution Console (SSE) */}
        <TerminalConsole batchId={activeBatchId} isProcessing={isProcessing} />

        {/* STEP 1: MULTI-FILE INGESTION & DATA PROFILING INSPECTION */}
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

        {/* STEP 2: AI SHEET RELEVANCE & SUB-TAB FILTERING + HUMAN TOGGLES */}
        {pipelineStep === 2 && (
          <SheetDiscoveryView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(3)}
            onReprocessSuccess={handleReprocessSuccess}
          />
        )}

        {/* STEP 3: LLM COLUMN MAPPING MATRIX + HUMAN DROPDOWNS */}
        {pipelineStep === 3 && (
          <ColumnMappingView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(4)}
            onReprocessSuccess={handleReprocessSuccess}
          />
        )}

        {/* STEP 4: STATUS NORMALIZATION + HUMAN CATEGORY DROPDOWNS */}
        {pipelineStep === 4 && (
          <StatusNormalizationView
            batchId={activeBatchId}
            onNext={() => setPipelineStep(5)}
            onReprocessSuccess={handleReprocessSuccess}
          />
        )}

        {/* STEP 5: DETERMINISTIC 3-WAY ORDER RECONCILIATION */}
        {pipelineStep === 5 && (
          <ReconciliationView reconciliation={reconciliation} />
        )}

        {/* STEP 6: AI GOVERNANCE QUEUE & FINANCE Q&A CONSOLE */}
        {pipelineStep === 6 && (
          <div className="space-y-6">
            <ExceptionsView
              exceptions={exceptions}
              batchId={activeBatchId}
              onExceptionResolved={() => fetchBatchData(activeBatchId)}
              onNext={() => {}}
            />
            <FinanceQAChat batchId={activeBatchId} />
          </div>
        )}
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-500 bg-white font-medium">
        FINANCE CONTROLLER AI • Enterprise System • Powered by FastAPI, LangGraph & Local LLM (qwen2.5:3b)
      </footer>
    </div>
  );
}
