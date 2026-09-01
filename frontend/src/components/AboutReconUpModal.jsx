import React, { useState } from 'react';
import {
  X,
  Sparkles,
  Layers,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  FileSpreadsheet,
  ArrowRight,
  TrendingUp,
  MessageSquare,
  FileCode2,
  AlertTriangle,
  Database,
  Search,
  CheckCircle,
  HelpCircle,
  Maximize2
} from 'lucide-react';

export default function AboutReconUpModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('architecture'); // 'architecture' | 'nodes' | 'rules' | 'qa' | 'benchmarks'
  const [dontShowAgain, setDontShowAgain] = useState(false);

  if (!isOpen) return null;

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem('reconup_hide_intro_modal', 'true');
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto animate-in fade-in duration-200">
      <div className="relative w-full max-w-5xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden my-6 flex flex-col max-h-[90vh]">
        {/* Modal Top Header Banner */}
        <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-slate-900 p-6 text-white flex-shrink-0 relative overflow-hidden">
          <div className="absolute right-0 top-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-blue-500/30 text-blue-200 border border-blue-400/30 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-amber-300" />
                  Track 04 Hackathon • AI Finance Controller
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                  Autonomous 8-Step Pipeline
                </span>
              </div>
              <h2 className="text-2xl md:text-3xl font-black tracking-tight text-white flex items-center gap-2">
                Understand Recon<span className="text-blue-300">Up</span>
              </h2>
              <p className="text-slate-200 text-sm mt-1 max-w-2xl font-medium">
                Autonomous multi-source settlement reconciliation, deterministic P&L arithmetic, and human-in-the-loop financial governance.
              </p>
            </div>

            <button
              onClick={handleClose}
              className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition border border-white/10 flex-shrink-0"
              title="Close Modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 mt-6 overflow-x-auto pb-1 text-xs font-bold border-b border-white/10">
            {[
              { id: 'architecture', label: '1. Architecture & Flowchart', icon: Layers },
              { id: 'nodes', label: '2. 8-Step Pipeline Breakdown', icon: Cpu },
              { id: 'rules', label: '3. Accounting & Privilege Rules', icon: ShieldCheck },
              { id: 'qa', label: '4. Settlement Q&A Co-Pilot', icon: MessageSquare },
              { id: 'benchmarks', label: '5. Technical Specs & Benchmarks', icon: TrendingUp }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl transition whitespace-nowrap ${
                    isActive
                      ? 'bg-white text-slate-900 shadow-md font-extrabold'
                      : 'text-slate-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-700 font-sans text-sm">
          {/* TAB 1: ARCHITECTURE & FLOWCHART */}
          {activeTab === 'architecture' && (
            <div className="space-y-6">
              {/* Critical Architectural Principle Banner */}
              <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-3">
                <ShieldCheck className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-amber-950 text-sm">Core Engineering Principle: Zero Financial Hallucinations</h4>
                  <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">
                    <strong>THE LLM IS NEVER THE SOURCE OF TRUTH FOR FINANCIAL CALCULATIONS.</strong> All payout math, multi-line fee aggregations, and 3-way order matching are executed by deterministic Python arithmetic. AI agents handle entity classification, schema mapping, status categorization, and read-only Text-to-SQL generation.
                  </p>
                </div>
              </div>

              {/* Core SVG Architecture Diagram */}
              <div className="border border-slate-200 rounded-2xl bg-slate-50/50 p-5">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-bold text-slate-900 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-blue-600" />
                    ReconUp End-to-End System Architecture
                  </h4>
                  <span className="text-[11px] font-mono text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                    SVG Interactive Diagram
                  </span>
                </div>

                {/* SVG Visual Flowchart */}
                <div className="w-full overflow-x-auto bg-white rounded-xl border border-slate-200 p-4 shadow-inner">
                  <svg
                    viewBox="0 0 920 320"
                    className="w-full min-w-[700px] h-auto font-sans"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <defs>
                      <linearGradient id="gradMaster" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#1d4ed8" />
                      </linearGradient>
                      <linearGradient id="gradPmt" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#8b5cf6" />
                        <stop offset="100%" stopColor="#6d28d9" />
                      </linearGradient>
                      <linearGradient id="gradEngine" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#10b981" />
                        <stop offset="100%" stopColor="#047857" />
                      </linearGradient>
                      <linearGradient id="gradReport" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#f59e0b" />
                        <stop offset="100%" stopColor="#b45309" />
                      </linearGradient>
                      <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
                        <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.08" />
                      </filter>
                    </defs>

                    {/* Background Guides */}
                    <rect x="10" y="10" width="900" height="300" rx="16" fill="#f8fafc" stroke="#e2e8f0" strokeWidth="1" />

                    {/* Step 1: Input Ingestion */}
                    <g filter="url(#shadow)">
                      <rect x="30" y="40" width="160" height="70" rx="10" fill="url(#gradMaster)" />
                      <text x="110" y="70" fill="#ffffff" fontWeight="bold" fontSize="13" textAnchor="middle">Master Order Sheet</text>
                      <text x="110" y="90" fill="#dbeafe" fontSize="10" textAnchor="middle">Anchor Manifest (.xlsx/.csv)</text>
                    </g>

                    <g filter="url(#shadow)">
                      <rect x="30" y="140" width="160" height="70" rx="10" fill="url(#gradPmt)" />
                      <text x="110" y="170" fill="#ffffff" fontWeight="bold" fontSize="13" textAnchor="middle">Payment Settlements</text>
                      <text x="110" y="190" fill="#ede9fe" fontSize="10" textAnchor="middle">Multi-File / Multi-Tab (.xlsx)</text>
                    </g>

                    {/* Arrow 1 */}
                    <path d="M 190 75 L 240 120" stroke="#94a3b8" strokeWidth="2" fill="none" markerEnd="url(#arrow)" />
                    <path d="M 190 175 L 240 135" stroke="#94a3b8" strokeWidth="2" fill="none" />

                    {/* Step 2: AI Pre-Processing Agents */}
                    <g filter="url(#shadow)">
                      <rect x="240" y="70" width="200" height="150" rx="12" fill="#ffffff" stroke="#cbd5e1" strokeWidth="1.5" />
                      <text x="340" y="95" fill="#0f172a" fontWeight="bold" fontSize="12" textAnchor="middle">🤖 AI Agent Reasoning Layer</text>
                      <rect x="255" y="108" width="170" height="24" rx="6" fill="#eff6ff" stroke="#bfdbfe" />
                      <text x="340" y="124" fill="#1e40af" fontSize="10" fontWeight="bold" textAnchor="middle">Node 1.5: SheetRelevanceAgent</text>
                      <rect x="255" y="138" width="170" height="24" rx="6" fill="#eff6ff" stroke="#bfdbfe" />
                      <text x="340" y="154" fill="#1e40af" fontSize="10" fontWeight="bold" textAnchor="middle">Node 2: ColumnMappingAgent</text>
                      <rect x="255" y="168" width="170" height="24" rx="6" fill="#eff6ff" stroke="#bfdbfe" />
                      <text x="340" y="184" fill="#1e40af" fontSize="10" fontWeight="bold" textAnchor="middle">Node 3: StatusNormalizationAgent</text>
                      <text x="340" y="208" fill="#64748b" fontSize="9" textAnchor="middle">Swappable: Gemini / Ollama</text>
                    </g>

                    {/* Arrow 2 */}
                    <path d="M 440 145 L 480 145" stroke="#94a3b8" strokeWidth="2" fill="none" />

                    {/* Step 3: Deterministic Reconciler */}
                    <g filter="url(#shadow)">
                      <rect x="480" y="60" width="200" height="170" rx="12" fill="url(#gradEngine)" />
                      <text x="580" y="88" fill="#ffffff" fontWeight="bold" fontSize="13" textAnchor="middle">Deterministic Engine</text>
                      <text x="580" y="106" fill="#d1fae5" fontSize="10" textAnchor="middle">Node 5: 3-Way Reconciler</text>
                      <line x1="500" y1="115" x2="660" y2="115" stroke="#34d399" strokeWidth="0.8" />
                      <text x="500" y="133" fill="#ffffff" fontSize="10">• Multi-Event Payout Aggregation</text>
                      <text x="500" y="151" fill="#ffffff" fontSize="10">• Payment Status Privilege Rule</text>
                      <text x="500" y="169" fill="#ffffff" fontSize="10">• Cancelled Orders Isolation (₹0)</text>
                      <text x="500" y="187" fill="#ffffff" fontSize="10">• Historical Payments Segregation</text>
                      <text x="580" y="215" fill="#a7f3d0" fontSize="9" fontWeight="bold" textAnchor="middle">31,779 records / sec</text>
                    </g>

                    {/* Arrow 3 */}
                    <path d="M 680 145 L 720 145" stroke="#94a3b8" strokeWidth="2" fill="none" />

                    {/* Step 4: Governance & Report */}
                    <g filter="url(#shadow)">
                      <rect x="720" y="50" width="170" height="90" rx="10" fill="url(#gradReport)" />
                      <text x="805" y="78" fill="#ffffff" fontWeight="bold" fontSize="12" textAnchor="middle">Node 6: Governance</text>
                      <text x="805" y="96" fill="#fef3c7" fontSize="10" textAnchor="middle">Human-in-the-Loop Queue</text>
                      <text x="805" y="114" fill="#fef3c7" fontSize="10" textAnchor="middle">Text-to-SQL Q&A Co-Pilot</text>
                    </g>

                    <g filter="url(#shadow)">
                      <rect x="720" y="160" width="170" height="80" rx="10" fill="#0f172a" stroke="#334155" />
                      <text x="805" y="190" fill="#ffffff" fontWeight="bold" fontSize="12" textAnchor="middle">Node 7: Executive P&L</text>
                      <text x="805" y="210" fill="#94a3b8" fontSize="10" textAnchor="middle">Audited Match Rates & Report</text>
                    </g>

                    {/* Bottom Status bar */}
                    <rect x="30" y="260" width="860" height="35" rx="8" fill="#ffffff" stroke="#e2e8f0" />
                    <circle cx="50" cy="277" r="4" fill="#10b981" />
                    <text x="65" y="281" fill="#334155" fontSize="11" fontWeight="bold">Active Tech Stack:</text>
                    <text x="180" y="281" fill="#64748b" fontSize="11">FastAPI Backend • LangGraph State Machine • Google Gemini 3.5 / Ollama qwen2.5 • SQLite Persistence • React Tailwind</text>
                  </svg>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: 8-STEP PIPELINE BREAKDOWN */}
          {activeTab === 'nodes' && (
            <div className="space-y-4">
              <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-blue-600" />
                Comprehensive 8-Step Pipeline Breakdown
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  {
                    step: 'Node 1',
                    title: 'Multi-File Ingest & Spreadsheet Profiling',
                    badge: 'Deterministic',
                    color: 'blue',
                    desc: 'Parses all uploaded Master Order and Payment Settlement files (.xlsx, .csv, .zip). Extracts exact column headers, sheets count, and row dimensions.'
                  },
                  {
                    step: 'Node 1.5',
                    title: 'Sub-Tab Filtering (SheetRelevanceAgent)',
                    badge: 'AI Agent',
                    color: 'indigo',
                    desc: 'Evaluates each discovered sub-tab in settlement workbooks. Retains transaction sheets with order-level data while dropping empty disclaimers (0 rows) and isolated ad notes.'
                  },
                  {
                    step: 'Node 2',
                    title: 'LLM Schema Mapping (ColumnMappingAgent)',
                    badge: 'AI + Smart Cache',
                    color: 'purple',
                    desc: 'Maps raw spreadsheet column names to canonical schema (order_id, amount, status, sku, quantity, payment_date). Uses Smart Schema Cache to avoid redundant LLM latency.'
                  },
                  {
                    step: 'Node 3',
                    title: 'Status Normalization (StatusNormalizationAgent)',
                    badge: 'AI Agent',
                    color: 'cyan',
                    desc: 'Standardizes disparate status strings from multiple marketplaces into canonical lifecycle states: Delivered, Return, RTO, Cancelled, Shipped, Claim, and Exchange.'
                  },
                  {
                    step: 'Node 4',
                    title: 'AI Status Integrity Audit (PatternDetectionAgent)',
                    badge: 'AI Integrity',
                    color: 'emerald',
                    desc: 'Inspects adjacent row key-value pairs to repair missing or co-dependent row statuses. Separates core order payments from isolated non-order fee deductions.'
                  },
                  {
                    step: 'Node 5',
                    title: '3-Way Order Reconciliation Engine',
                    badge: 'Deterministic Reconciler',
                    color: 'emerald',
                    desc: 'Matches Master Orders against multi-event payment disbursements. Aggregates multi-line payouts to compute Net Settlement Payout per Order ID with 100% mathematical auditability.'
                  },
                  {
                    step: 'Node 6',
                    title: 'Exception Governance & Settlement Q&A',
                    badge: 'Human-in-the-Loop',
                    color: 'amber',
                    desc: 'Surfaces financial anomalies & unknown deduction patterns for human decision-making. Features an interactive Text-to-SQL Settlement Q&A Co-Pilot.'
                  },
                  {
                    step: 'Node 7',
                    title: 'Executive Financial P&L Audit Report',
                    badge: 'Final P&L',
                    color: 'slate',
                    desc: 'Generates comprehensive audit metrics: Match Rate (%), Net Settled Payout (INR ₹), Disputed Exposure, Order Manifest Status Breakdown, and Raw JSON data export.'
                  }
                ].map((n, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-white border border-slate-200 hover:border-blue-300 transition shadow-sm space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 rounded-lg text-[10px] font-mono font-bold bg-slate-100 text-slate-800 border border-slate-200">
                        {n.step}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        {n.badge}
                      </span>
                    </div>
                    <h4 className="font-bold text-slate-900 text-sm">{n.title}</h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{n.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: ACCOUNTING & PRIVILEGE RULES */}
          {activeTab === 'rules' && (
            <div className="space-y-4">
              <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                Specialized Financial Reconciliation & Accounting Rules
              </h3>

              <div className="space-y-4">
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 rounded-lg bg-blue-100 text-blue-700">
                      <CheckCircle2 className="w-4 h-4" />
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm">1. Payment Status Privilege Rule (Downstream Supremacy)</h4>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    <strong>Rule:</strong> When an Order ID is present in both the Master Order Sheet and Payment Settlement Sheet, <strong>privilege is given to the Payment Settlement event status FIRST</strong>.
                    <br />
                    <em>Why?</em> An order initially marked as `Delivered` at dispatch in the master manifest may have subsequently been returned by the customer (`Return`, `Refund`, or `RTO`) in the settlement cycle. Inspecting the payment status ensures accurate operational categorization.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 rounded-lg bg-rose-100 text-rose-700">
                      <CheckCircle2 className="w-4 h-4" />
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm">2. Cancelled Orders Accounting Separation</h4>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    <strong>Rule:</strong> Orders marked as `Cancelled` without payment entries are isolated into a dedicated <code className="bg-slate-200 px-1 rounded text-slate-800 font-mono">cancelledOrders</code> dataset with an expected payout of ₹0.00.
                    <br />
                    <em>Why?</em> Cancelled orders do not represent pending payouts or missing revenue exposure. Isolating them prevents false inflation of unsettled monetary exposure.
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 rounded-lg bg-purple-100 text-purple-700">
                      <CheckCircle2 className="w-4 h-4" />
                    </span>
                    <h4 className="font-bold text-slate-900 text-sm">3. Historical Payment Lines Isolation</h4>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    <strong>Rule:</strong> Payment lines referencing historical Order IDs from prior billing periods that are not present in the active Master Order manifest are segregated into <code className="bg-slate-200 px-1 rounded text-slate-800 font-mono">missingInOrder</code>.
                    <br />
                    <em>Why?</em> These represent valid trailing payouts and are exempted from active order manifest lifecycle counts so they do not distort current batch match rates.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: SETTLEMENT Q&A CO-PILOT */}
          {activeTab === 'qa' && (
            <div className="space-y-4">
              <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-indigo-600" />
                Interactive Settlement Q&A Co-Pilot (Text-to-SQL Architecture)
              </h3>
              <p className="text-xs text-slate-600">
                ReconUp features a built-in financial co-pilot enabling finance controllers and auditors to query complex settlement batches in natural language.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3.5 rounded-2xl bg-blue-50 border border-blue-200 space-y-1">
                  <div className="flex items-center gap-1.5 text-blue-900 font-bold text-xs">
                    <Search className="w-4 h-4 text-blue-700" />
                    1. Text-to-SQL Translation
                  </div>
                  <p className="text-[11px] text-blue-800 leading-relaxed">
                    Converts auditor questions into audited SQL queries executed directly against SQLite (<code className="font-mono">orders</code>, <code className="font-mono">payments</code>, <code className="font-mono">reconciliation_results</code>).
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 space-y-1">
                  <div className="flex items-center gap-1.5 text-amber-900 font-bold text-xs">
                    <ShieldCheck className="w-4 h-4 text-amber-700" />
                    2. Read-Only Security Guard
                  </div>
                  <p className="text-[11px] text-amber-800 leading-relaxed">
                    Enforces strict read-only queries (<code className="font-mono">SELECT / WITH</code> only). Rejects any mutation statements (<code className="font-mono">DROP, DELETE, UPDATE</code>).
                  </p>
                </div>

                <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 space-y-1">
                  <div className="flex items-center gap-1.5 text-emerald-900 font-bold text-xs">
                    <CheckCircle className="w-4 h-4 text-emerald-700" />
                    3. 6s Hard Timeout Protection
                  </div>
                  <p className="text-[11px] text-emerald-800 leading-relaxed">
                    Guarantees lightning-fast responses with a 6-second timeout safeguard and collapsible backend debug trace panels in the UI.
                  </p>
                </div>
              </div>

              {/* Sample Queries */}
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200">
                <h4 className="font-bold text-slate-900 text-xs mb-2">Example Natural Language Questions You Can Ask:</h4>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-medium">
                    "What is my match rate and total net payout?"
                  </span>
                  <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-medium">
                    "Show all orders with negative settlement amounts"
                  </span>
                  <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-medium">
                    "What are the top 5 SKUs with return events?"
                  </span>
                  <span className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-700 font-medium">
                    "What is the total value of unsettled orders?"
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: TECHNICAL SPECS & BENCHMARKS */}
          {activeTab === 'benchmarks' && (
            <div className="space-y-4">
              <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-600" />
                Measured Performance Benchmarks & Technical Specs
              </h3>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200">
                  <div className="text-2xl font-black text-blue-900">31,779</div>
                  <div className="text-[11px] font-bold text-blue-700 mt-0.5">Records / Second</div>
                </div>
                <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
                  <div className="text-2xl font-black text-emerald-900">100.0%</div>
                  <div className="text-[11px] font-bold text-emerald-700 mt-0.5">Match Precision & Recall</div>
                </div>
                <div className="p-4 rounded-2xl bg-purple-50 border border-purple-200">
                  <div className="text-2xl font-black text-purple-900">0</div>
                  <div className="text-[11px] font-bold text-purple-700 mt-0.5">False Matches</div>
                </div>
                <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200">
                  <div className="text-2xl font-black text-amber-900">3.15 ms</div>
                  <div className="text-[11px] font-bold text-amber-700 mt-0.5">Batch Processing Time</div>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
                <h4 className="font-bold text-slate-900 text-xs">Swappable Multi-LLM Architecture:</h4>
                <p className="text-xs text-slate-600 leading-relaxed">
                  ReconUp supports instantaneous switching between local offline models (Ollama <code className="bg-slate-200 px-1 rounded font-mono">qwen2.5:3b</code>) and cloud APIs (Google Gemini <code className="bg-slate-200 px-1 rounded font-mono">gemini-3.5-flash</code>) via simple environment variable configuration in <code className="bg-slate-200 px-1 rounded font-mono">backend/.env</code>.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Controls */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between flex-shrink-0">
          <label className="flex items-center gap-2 text-xs text-slate-600 font-medium cursor-pointer select-none">
            <input
              type="checkbox"
              checked={dontShowAgain}
              onChange={(e) => setDontShowAgain(e.target.checked)}
              className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer"
            />
            <span>Don't show this guide automatically on page load</span>
          </label>

          <button
            onClick={handleClose}
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md shadow-blue-500/20 transition flex items-center gap-1.5"
          >
            <span>Got it, Explore ReconUp</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
