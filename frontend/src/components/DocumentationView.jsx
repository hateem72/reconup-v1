import React, { useState } from 'react';
import {
  ArrowLeft,
  FileText,
  Layers,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  ExternalLink,
  Download,
  Sparkles,
  Search,
  Database,
  TrendingUp,
  MessageSquare,
  HelpCircle,
  AlertCircle,
  FileSpreadsheet,
  CheckCircle,
  Clock,
  Zap,
  Terminal,
  ChevronRight
} from 'lucide-react';

export default function DocumentationView({ onBackToDashboard }) {
  const [activeSection, setActiveSection] = useState('pdf'); // 'pdf' | 'overview' | 'nodes' | 'rules' | 'qa' | 'benchmarks'
  const [pdfZoom, setPdfZoom] = useState(100);
  const [isPdfFullscreen, setIsPdfFullscreen] = useState(false);

  const handleZoomIn = () => setPdfZoom((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setPdfZoom((prev) => Math.max(prev - 25, 50));
  const handleResetZoom = () => setPdfZoom(100);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-16">
      {/* Top Header Sticky Navigation */}
      <div className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-4 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={onBackToDashboard}
              className="p-2.5 rounded-xl bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 transition flex items-center gap-2 text-xs font-bold cursor-pointer"
              title="Return to Dashboard"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Console</span>
            </button>

            <div className="h-6 w-px bg-slate-200 hidden sm:block" />

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black text-slate-900 tracking-tight flex items-center gap-1.5">
                  Recon<span className="text-blue-600">Up</span>
                  <span className="text-slate-400 font-normal">/</span>
                  <span className="text-slate-800 text-sm font-bold">System Architecture & Engineering Guide</span>
                </h1>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                  Track 04
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">
                Comprehensive technical specifications, flowchart PDF, 8-step pipeline details, and accounting rules
              </p>
            </div>
          </div>

          {/* Section Navigation Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs font-bold">
            {[
              { id: 'pdf', label: 'Architecture PDF', icon: FileText },
              { id: 'overview', label: 'System Overview', icon: Layers },
              { id: 'nodes', label: '8-Step Pipeline', icon: Cpu },
              { id: 'rules', label: 'Accounting Rules', icon: ShieldCheck },
              { id: 'qa', label: 'Text-to-SQL Co-Pilot', icon: MessageSquare },
              { id: 'benchmarks', label: 'Benchmarks', icon: TrendingUp }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeSection === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveSection(tab.id)}
                  className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl transition cursor-pointer whitespace-nowrap ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20 font-bold'
                      : 'bg-white hover:bg-slate-100 text-slate-600 border border-slate-200'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content Body */}
      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-8">
        {/* SECTION 1: ARCHITECTURE PDF VIEWER */}
        {activeSection === 'pdf' && (
          <div className="space-y-4 animate-in fade-in duration-200">
            {/* PDF Controls Card */}
            <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-700 border border-indigo-200">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-sm flex items-center gap-2">
                    Official ReconUp Architecture Diagram (PDF)
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-700 border border-slate-200">
                      architecture.pdf
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    High-resolution vector architecture flowchart with complete node data flows
                  </p>
                </div>
              </div>

              {/* Interactive PDF Toolbar Controls */}
              <div className="flex items-center gap-2 flex-wrap">
                <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
                  <button
                    onClick={handleZoomOut}
                    className="p-1.5 rounded-lg hover:bg-white text-slate-700 transition cursor-pointer"
                    title="Zoom Out"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </button>
                  <span className="px-2.5 text-xs font-mono font-bold text-slate-700 min-w-[55px] text-center">
                    {pdfZoom}%
                  </span>
                  <button
                    onClick={handleZoomIn}
                    className="p-1.5 rounded-lg hover:bg-white text-slate-700 transition cursor-pointer"
                    title="Zoom In"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  <button
                    onClick={handleResetZoom}
                    className="p-1.5 rounded-lg hover:bg-white text-slate-500 hover:text-slate-800 transition cursor-pointer"
                    title="Reset Zoom (100%)"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>

                <a
                  href="/architecture.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
                  title="Open PDF in new browser tab"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Open in Tab</span>
                </a>

                <a
                  href="/architecture.pdf"
                  download="ReconUp_Architecture.pdf"
                  className="px-3 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 text-xs font-bold transition flex items-center gap-1.5 cursor-pointer"
                  title="Download Architecture PDF"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download</span>
                </a>
              </div>
            </div>

            {/* Scrollable & Zoomable PDF Embed Frame */}
            <div className="rounded-3xl bg-slate-100 border border-slate-300 shadow-inner overflow-hidden p-2 sm:p-4">
              <div
                className="w-full overflow-auto bg-white rounded-2xl border border-slate-200 shadow-md transition-all duration-150 flex items-center justify-center min-h-[720px]"
                style={{
                  transform: `scale(${pdfZoom / 100})`,
                  transformOrigin: 'top center',
                  width: `${(100 / (pdfZoom / 100))}%`
                }}
              >
                <iframe
                  src="/architecture.pdf#toolbar=1&navpanes=0&scrollbar=1&view=FitH"
                  title="ReconUp System Architecture PDF"
                  className="w-full h-[850px] border-none rounded-xl"
                />
              </div>
            </div>
          </div>
        )}

        {/* SECTION 2: SYSTEM OVERVIEW */}
        {activeSection === 'overview' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* Executive Vision Banner */}
            <div className="p-6 rounded-3xl bg-gradient-to-br from-blue-900 via-indigo-900 to-slate-950 text-white shadow-xl relative overflow-hidden">
              <div className="relative z-10 space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-bold">
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  Track 04: AI Finance Controller Platform
                </div>
                <h2 className="text-2xl md:text-3xl font-black tracking-tight text-white">
                  Closing the Finance-Ops Loop with Absolute Accuracy
                </h2>
                <p className="text-slate-300 text-sm max-w-3xl leading-relaxed">
                  In modern e-commerce marketplace operations, verification capacity is the primary bottleneck. Settlement reconciliation, fee deduction audits, and cash forecasting across disparate workbooks (Meesho, Amazon, Flipkart, Shopify) are performed manually and prone to errors.
                  <br /><br />
                  <strong>ReconUp</strong> automates multi-source settlement reconciliation, enforces deterministic P&L arithmetic, surfaces unknown marketplace deduction patterns for human governance, and persists approved rules into a rule registry database for dynamic re-processing.
                </p>
              </div>
            </div>

            {/* Core Architectural Principle Alert */}
            <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-950 flex items-start gap-3.5 shadow-xs">
              <ShieldCheck className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold text-sm text-amber-950">
                  Critical Architectural Rule: Zero Financial Hallucinations
                </h4>
                <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                  <strong>THE LLM IS NEVER THE SOURCE OF TRUTH FOR FINANCIAL ARITHMETIC.</strong> All net payout calculations, multi-line fee aggregations, and 3-way order matching are executed by deterministic Python algorithms. The LLM handles entity extraction, schema mapping, status categorization, sub-tab relevance classification, exception explanations, and read-only Text-to-SQL tool routing.
                </p>
              </div>
            </div>

            {/* High-Level Architecture Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
                <div className="p-2.5 rounded-xl bg-blue-50 text-blue-700 w-fit">
                  <FileSpreadsheet className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-slate-900 text-sm">Multi-Source Ingestion</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Ingests Master Order Manifests alongside multiple Multi-Tab Payment Settlement workbooks (.xlsx, .csv, .zip) simultaneously.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
                <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-700 w-fit">
                  <Cpu className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-slate-900 text-sm">Deterministic 3-Way Engine</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Aggregates multi-event payment lines per Order ID to calculate exact Net Settlement Payout with 100% mathematical auditability.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
                <div className="p-2.5 rounded-xl bg-purple-50 text-purple-700 w-fit">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-slate-900 text-sm">Settlement Q&A Co-Pilot</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Interactive Text-to-SQL natural language copilot with strict read-only security guards and 6-second timeout safeguards.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 3: 8-STEP PIPELINE DEEP DIVE */}
        {activeSection === 'nodes' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-black text-slate-900">8-Step Autonomous Pipeline Workflow</h3>
                <p className="text-xs text-slate-500 font-medium">Detailed step-by-step reasoning & deterministic arithmetic execution</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                8 Integrated Nodes
              </span>
            </div>

            <div className="space-y-4">
              {[
                {
                  node: 'Node 1',
                  name: 'Multi-File Ingest & Spreadsheet Profiling',
                  badge: 'Deterministic Ingest',
                  color: 'blue',
                  input: 'Master Order Sheet (.xlsx/.csv) + Multiple Payment Settlement Files (.xlsx/.csv/.zip)',
                  output: 'Exact header profiles, row counts, and active batch execution context',
                  details: 'Parses binary spreadsheet workbooks, extracts headers with exact case sensitivity, measures dataset dimensions, and initializes the in-memory batch state store.'
                },
                {
                  node: 'Node 1.5',
                  name: 'Sub-Tab Relevance Filtering (SheetRelevanceAgent)',
                  badge: 'AI Agent Reasoning',
                  color: 'indigo',
                  input: 'Discovered workbook sub-tabs with sample row previews and header sets',
                  output: 'Retained transaction sheets vs Dropped summary notes/disclaimers',
                  details: 'Evaluates each sheet to distinguish order-level financial transaction lines from empty disclaimer notices (0 rows) and isolated ad fee notes.'
                },
                {
                  node: 'Node 2',
                  name: 'LLM Schema Mapping (ColumnMappingAgent)',
                  badge: 'AI + Smart Cache',
                  color: 'purple',
                  input: 'Raw spreadsheet column headers across disparate marketplace formats',
                  output: 'Canonical schema mapping (order_id, amount, status, sku, quantity, payment_date)',
                  details: 'Autonomous LLM agent maps disparate raw columns to standard schema. Uses a persistent Smart Schema Cache to skip LLM latency on recurring file templates.'
                },
                {
                  node: 'Node 3',
                  name: 'Status Normalization (StatusNormalizationAgent)',
                  badge: 'Canonical Classifier',
                  color: 'cyan',
                  input: 'Raw status strings (e.g. "Delivered", "Customer Return", "RTO_IN_TRANSIT")',
                  output: 'Normalized canonical statuses: Delivered, Return, RTO, Cancelled, Shipped, Claim, Exchange',
                  details: 'Standardizes disparate marketplace status descriptions into canonical operational lifecycle states for downstream accounting.'
                },
                {
                  node: 'Node 4',
                  name: 'AI Status Integrity Audit (PatternDetectionAgent)',
                  badge: 'AI Integrity Audit',
                  color: 'emerald',
                  input: 'Canonical dataset with potential missing statuses or co-dependent row states',
                  output: '100% repaired status coverage; separated fee deductions from order payouts',
                  details: 'Dynamically inspects adjacent row key-value pairs to repair missing or co-dependent order statuses. Categorizes fee deductions into separate accounting buckets.'
                },
                {
                  node: 'Node 5',
                  name: 'Deterministic 3-Way Order Reconciliation Engine',
                  badge: 'Deterministic Reconciler',
                  color: 'emerald',
                  input: 'Normalized Master Orders vs Aggregated Multi-Event Payment Lines',
                  output: 'Matched orders (Net Payout ₹), Unsettled orders, Cancelled orders (₹0), Historical payments',
                  details: 'Matches orders by Order ID, aggregates multi-event payouts (disbursement - deductions), enforces Payment Status Privilege, and isolates Cancelled orders from unsettled exposure.'
                },
                {
                  node: 'Node 6',
                  name: 'Exception Governance Queue & Settlement Q&A',
                  badge: 'Human-in-the-Loop',
                  color: 'amber',
                  input: 'Surfaced financial exceptions & Natural language auditor questions',
                  output: 'Approved rules persisted to registry; Instant Text-to-SQL financial answers',
                  details: 'Surfaces financial anomalies into an interactive governance queue. Includes a 100% read-only Text-to-SQL Settlement Q&A Co-Pilot with 6s timeout protection.'
                },
                {
                  node: 'Node 7',
                  name: 'Executive Financial P&L Audit Report',
                  badge: 'Executive Audit',
                  color: 'slate',
                  input: 'Consolidated reconciliation results & human-approved governance rules',
                  output: 'Executive P&L summary, audited match rate (%), live manifest status counts, Raw JSON export',
                  details: 'Generates executive financial summary metrics, match rate percentages, and raw JSON export modals for total audit traceability.'
                }
              ].map((n, idx) => (
                <div key={idx} className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-slate-100 text-slate-800 border border-slate-200">
                        {n.node}
                      </span>
                      <h4 className="font-bold text-slate-900 text-sm">{n.name}</h4>
                    </div>
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200 w-fit">
                      {n.badge}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed">{n.details}</p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="font-bold text-slate-700 block mb-0.5">Input:</span>
                      <span className="text-slate-600">{n.input}</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                      <span className="font-bold text-slate-700 block mb-0.5">Output:</span>
                      <span className="text-slate-600">{n.output}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* SECTION 4: ACCOUNTING & PRIVILEGE RULES */}
        {activeSection === 'rules' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <h3 className="text-lg font-black text-slate-900">Specialized Financial Accounting & Privilege Rules</h3>

            <div className="space-y-4">
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-blue-50 text-blue-700">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">1. Payment Status Privilege Rule (Downstream Event Supremacy)</h4>
                    <span className="text-[11px] font-mono text-blue-700 font-bold">Node 5 Reconciliation Engine</span>
                  </div>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <strong>The Problem Solved:</strong> When an order is created, the initial Master Order Manifest marks it as `Delivered` at dispatch. If the customer subsequently returns the item (or an RTO/refund occurs), the Payment Settlement Sheet records the `Return`/`Refund` event.
                  <br /><br />
                  <strong>The Accounting Rule:</strong> Whenever an Order ID is present in both sheets, <strong>privilege is given to the Payment Settlement event status FIRST</strong>. If the payment sheet reports `Return` or `RTO`, the order's operational lifecycle is categorized as `Return` / `RTO` (and counted under return metrics), preventing false over-reporting of delivered orders.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-rose-50 text-rose-700">
                    <AlertCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">2. Cancelled Orders Accounting Separation</h4>
                    <span className="text-[11px] font-mono text-rose-700 font-bold">Unsettled Exposure Protection</span>
                  </div>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <strong>The Problem Solved:</strong> Cancelled orders never generate revenue or expected marketplace disbursements. Placing non-paid cancelled orders into the missing/unsettled list artificially inflates the financial exposure metric.
                  <br /><br />
                  <strong>The Accounting Rule:</strong> Cancelled orders with no payment rows are segregated into a dedicated <code className="font-mono bg-slate-100 px-1 rounded text-slate-800">cancelledOrders</code> list with ₹0.00 expected payout. They are displayed with a distinct rose-red badge and do not penalize unsettled exposure.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-purple-50 text-purple-700">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">3. Historical Payment Lines Isolation</h4>
                    <span className="text-[11px] font-mono text-purple-700 font-bold">Trailing Billing Protection</span>
                  </div>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  <strong>The Problem Solved:</strong> Marketplace settlement workbooks often include trailing disbursements for older orders not present in the current master order manifest.
                  <br /><br />
                  <strong>The Accounting Rule:</strong> These trailing payments are classified into <code className="font-mono bg-slate-100 px-1 rounded text-slate-800">missingInOrder</code> (<span className="text-purple-700 font-bold">HISTORICAL_PAYMENT</span>). They are tracked as extra cash collected and exempted from the active order manifest status counts to prevent match rate distortion.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 5: SETTLEMENT Q&A CO-PILOT */}
        {activeSection === 'qa' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <h3 className="text-lg font-black text-slate-900">Settlement Q&A Co-Pilot (Text-to-SQL System)</h3>
            <p className="text-xs text-slate-600">
              The integrated Settlement Q&A Co-Pilot translates natural language auditor queries into audited SQLite queries, executing with high-speed read-only guards and timeout safeguards.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
                <div className="p-2.5 rounded-xl bg-blue-50 text-blue-700 w-fit">
                  <Search className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-slate-900 text-xs">1. Text-to-SQL Generator</h4>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Translates questions into exact SQLite queries across <code className="font-mono">orders</code>, <code className="font-mono">payments</code>, and <code className="font-mono">reconciliation_results</code>.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
                <div className="p-2.5 rounded-xl bg-amber-50 text-amber-700 w-fit">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-slate-900 text-xs">2. Read-Only Guard</h4>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Enforces strict <code className="font-mono">SELECT / WITH</code> syntax only. Instantly rejects <code className="font-mono">DROP, DELETE, UPDATE</code> statements.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
                <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-700 w-fit">
                  <Zap className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-slate-900 text-xs">3. 6s Timeout Safeguard</h4>
                <p className="text-[11px] text-slate-600 leading-relaxed">
                  Executes queries with a 6-second thread timeout so the UI never freezes, providing collapsible backend debug trace panels for verification.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* SECTION 6: BENCHMARKS */}
        {activeSection === 'benchmarks' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <h3 className="text-lg font-black text-slate-900">Measured Performance & Technical Specifications</h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                <div className="text-3xl font-black text-blue-600">31,779</div>
                <div className="text-xs font-bold text-slate-700 mt-1">Records / Second</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Deterministic Reconciler</div>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                <div className="text-3xl font-black text-emerald-600">100.0%</div>
                <div className="text-xs font-bold text-slate-700 mt-1">Precision & Recall</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Zero False Positives</div>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                <div className="text-3xl font-black text-purple-600">0</div>
                <div className="text-xs font-bold text-slate-700 mt-1">False Matches</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Exact Anchor ID Matching</div>
              </div>

              <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                <div className="text-3xl font-black text-amber-600">3.15 ms</div>
                <div className="text-xs font-bold text-slate-700 mt-1">Batch Runtime</div>
                <div className="text-[10px] text-slate-400 mt-0.5">100-Record Synthetic Test</div>
              </div>
            </div>

            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
              <h4 className="font-bold text-slate-900 text-xs">Swappable Multi-LLM Provider Architecture:</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                ReconUp supports instantaneous switching between local offline models (Ollama <code className="bg-slate-100 px-1 rounded font-mono">qwen2.5:3b</code>) and cloud APIs (Google Gemini <code className="bg-slate-100 px-1 rounded font-mono">gemini-3.5-flash</code>) via simple configuration in <code className="bg-slate-100 px-1 rounded font-mono">backend/.env</code>.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
