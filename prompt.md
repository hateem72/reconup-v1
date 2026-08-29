# TLDraw MCP System Architecture Flowchart Prompt

> **Purpose**: Use this prompt with the [tldraw-mcp](https://github.com/dpunj/tldraw-mcp) server to automatically draw a complete, color-coded, professional system architecture whiteboard for the **Agentic AI Finance Controller** platform.

---

## 🎯 Master Prompt for AI Agents with tldraw-mcp

```	ext
You are an expert system architect and visual designer using the tldraw-mcp toolset.
Create a comprehensive, beautifully organized, color-coded system architecture whiteboard for the 'Agentic AI Finance Controller' application.

Use the tldraw-mcp tools (create_frame, create_shape, connect_shapes, create_arrow, zoom_to_fit) with clean spacing (no overlapping shapes), distinct color semantics, structured frames, and labeled arrows.

================================================================================
CANVAS STRUCTURE & COLOR SEMANTICS
================================================================================
• Frame 1 [Top-Left]: 'Frontend Presentation Layer (React + Vite - Port 3000)' -> color: 'blue', fill: 'semi'
• Frame 2 [Top-Right]: 'FastAPI Gateway & SSE Stream (Port 8000)' -> color: 'violet', fill: 'semi'
• Frame 3 [Center-Wide]: 'LangGraph 7-Stage Multi-Agent Reconciliation Pipeline' -> color: 'grey', fill: 'none'
• Frame 4 [Bottom-Left]: 'High-Speed Caching Layer (Redis + RAM Fallback)' -> color: 'red', fill: 'semi'
• Frame 5 [Bottom-Center]: 'Persistence Layer (SQLite / PostgreSQL + SQLAlchemy ORM)' -> color: 'black', fill: 'semi'
• Frame 6 [Bottom-Right]: 'Local & Cloud AI Model Fleet (Ollama / OpenAI / Gemini)' -> color: 'orange', fill: 'semi'
• Frame 7 [Far-Right]: 'Centralized Environment Config (.env & config.py)' -> color: 'yellow', fill: 'semi'

================================================================================
DETAILED NODE & SHAPE SPECIFICATIONS
================================================================================

1. FRAME: FRONTEND LAYER (X: 50, Y: 50, W: 1100, H: 450)
   Create rectangle cards inside for all 12 UI components:
   - [50, 100] Navbar.jsx (System Reset, Active Batch ID) [color: 'blue']
   - [250, 100] AgentMonitorBar.jsx (Live Fleet & Sheet Metrics) [color: 'blue']
   - [480, 100] PipelineStepper.jsx (6-Stage SSE Glowing Status) [color: 'blue']
   - [750, 100] TerminalConsole.jsx (Real-Time SSE Live Logs) [color: 'violet']
   - [50, 240] Step 1: UploadSection.jsx (Multi-File Ingestion Dropzone) [color: 'light-blue']
   - [250, 240] Step 1 Result: IngestInspectionView.jsx (Header & Sheet Profiler) [color: 'light-blue']
   - [480, 240] Step 2: SheetDiscoveryView.jsx (Human Sub-Tab Retention Toggle) [color: 'yellow']
   - [750, 240] Step 3: ColumnMappingView.jsx (AI Schema Dropdown Overrides) [color: 'yellow']
   - [50, 360] Step 4: StatusNormalizationView.jsx (Status Category Correction) [color: 'yellow']
   - [250, 360] Step 5: ReconciliationView.jsx (Settlement Match Table & Export) [color: 'green']
   - [480, 360] Step 6: ExceptionsView.jsx (AI Exception Governance Queue) [color: 'red']
   - [750, 360] Step 6: FinanceQAChat.jsx (Grounded AI Financial Assistant) [color: 'orange']

2. FRAME: FASTAPI API GATEWAY (X: 1200, Y: 50, W: 850, H: 450)
   Create API cards [color: 'violet', fill: 'semi']:
   - [1220, 100] POST /api/batches (Buffer bytes in 5ms, spawn async task)
   - [1480, 100] GET /api/batches/{id}/stream (SSE text/event-stream)
   - [1720, 100] POST /api/batches/{id}/reprocess (Reprocess from Node N)
   - [1220, 220] GET /api/reconciliation/{id} (Match stats & matrix)
   - [1480, 220] GET /api/exceptions/{id} & POST /resolve (Governance)
   - [1720, 220] POST /api/qa (Natural language finance queries)
   - [1220, 340] POST /api/reset (Hard reset: clear DB & flush Redis)
   - [1480, 340] GET /api/health (Health check & runtime status)

3. FRAME: LANGGRAPH 7-STAGE PIPELINE (X: 50, Y: 550, W: 2000, H: 600)
   Create 7 pipeline node cards from left to right:
   - NODE 1 (X: 100, Y: 620, W: 220, H: 160) [color: 'orange']
     Title: 'NODE 1: Ingest & Header Profiling'
     Text: '• parse_excel_bytes (RAM)\n• header_detector (True Header)\n• profiler (Row count, Nulls)\n• Initial Role Classification'
   
   - NODE 1.5 (X: 360, Y: 620, W: 220, H: 160) [color: 'orange']
     Title: 'NODE 1.5: Sheet Relevance Agent'
     Text: '• Agent: SheetRelevanceAgent\n• LLM: Ollama qwen2.5:3b\n• Evaluates headers & 2 samples\n• REQUIRED vs NOT_REQUIRED'

   - NODE 2 (X: 620, Y: 620, W: 240, H: 160) [color: 'orange']
     Title: 'NODE 2: Column Mapping Agent'
     Text: '• Agent: ColumnMappingAgent\n• SHA-256 Schema Fingerprint\n• Redis Cache Check (24h TTL)\n• Python Structural Guardrails'

   - NODE 3 (X: 900, Y: 620, W: 230, H: 160) [color: 'orange']
     Title: 'NODE 3: Status Normalization'
     Text: '• Agent: StatusNormalizationAgent\n• Deduplicated Unique Set\n• 50k rows -> 6 unique -> 1 LLM call\n• O(n) canonical status map'

   - NODE 4 (X: 1170, Y: 620, W: 220, H: 160) [color: 'orange']
     Title: 'NODE 4: Pattern Detection'
     Text: '• Agent: PatternDetectionAgent\n• Compares vs rule_registry\n• Detects unknown deductions\n• Proposes auto-learned rules'

   - NODE 5 (X: 1430, Y: 600, W: 260, H: 200) [color: 'green', fill: 'solid']
     Title: 'NODE 5: Reconciliation Engine'
     Text: '⭐ 100% DETERMINISTIC - NO AI\n• order_normalizer (CanonicalOrder)\n• payment_normalizer (Payment)\n• Tolerance Match (0.01 INR)\n• MATCHED / OVER / UNDER / UNSETTLED'

   - NODE 6 (X: 1730, Y: 620, W: 240, H: 160) [color: 'red']
     Title: 'NODE 6: Exception Governance & QA'
     Text: '• evaluate_batch_exceptions\n• Severity: HIGH / MED / LOW\n• Exposure calculation\n• Human Accept / Reject / Escalate\n• Grounded QA Assistant'

4. INFRASTRUCTURE & BACKEND SERVICES (Y: 1200)
   - FRAME: REDIS CACHE (X: 50, Y: 1200, W: 550, H: 300) [color: 'red']
     Title: 'Redis Distributed Cache Engine (redis_client.py)'
     Text: '• Schema Fingerprint Key: schema:{role}:{sha256}\n• 24-Hour Automatic TTL Expiration\n• Auto In-Memory Python RAM Fallback\n• One-Click Pattern Flush on Hard Reset'
   
   - FRAME: SQLITE DATABASE (X: 650, Y: 1200, W: 650, H: 300) [color: 'black']
     Title: 'Relational Database (SQLAlchemy ORM)'
     Text: 'Tables: BatchModel, FileModel, SheetModel, OrderModel, PaymentModel, ReconciliationResultModel, ExceptionModel, AgentDecisionModel, ReportModel, AuditEventModel\n• Zero-Code Swap to PostgreSQL via DATABASE_URL'

   - FRAME: LLM FLEET (X: 1350, Y: 1200, W: 450, H: 300) [color: 'orange']
     Title: 'Multi-Provider LLM Engine (llm_factory.py)'
     Text: '• Active: Local Ollama (qwen2.5:3b) at :11434\n• Swappable via .env: OpenAI (gpt-4o-mini), Gemini (gemini-1.5-flash), Anthropic (claude-3-5-sonnet)'

   - FRAME: CONFIG (X: 1850, Y: 1200, W: 350, H: 300) [color: 'yellow']
     Title: 'Centralized Config (.env & config.py)'
     Text: '• REDIS_URL & TTL\n• LLM_PROVIDER & MODEL\n• API Keys & OLLAMA_BASE_URL\n• DATABASE_URL'

================================================================================
ARROWS & DATA FLOW CONNECTIONS
================================================================================
1. [UploadSection] -> [POST /api/batches] (Label: 'Upload Raw Files (.xlsx, .csv, .zip)')
2. [POST /api/batches] -> [Node 1] (Label: 'Async Worker Spawn (~5ms return)')
3. [GET /api/batches/{id}/stream] -> [TerminalConsole & PipelineStepper] (Label: 'SSE Real-Time Stream (NODE_START, LOGS, COMPLETE)')
4. [Node 1] -> [Node 1.5] (Label: 'raw_datasets[]')
5. [Node 1.5] -> [Node 2] (Label: 'retained_datasets[]')
6. [Node 2] -> [Node 3] (Label: 'column_mappings{}')
7. [Node 3] -> [Node 4] (Label: 'normalized_orders[]')
8. [Node 4] -> [Node 5] (Label: 'verified_patterns[]')
9. [Node 5] -> [Node 6] (Label: 'reconciliation_matrix')
10. [Redis Frame] -> [Node 2] (Label: '⚡ CACHE HIT (0s LLM Latency Bypass Arrow)' [color: 'yellow'])
11. [Node 5] -> [SQLite Frame] (Label: 'Persist Canonical Orders, Payments & Match Results' [color: 'green'])
12. [Human Override Loops - Yellow Curved Arrows]:
    • [SheetDiscoveryView] -> [POST /reprocess] -> [Node 2] (Label: 'Override Sheet Selection')
    • [ColumnMappingView] -> [POST /reprocess] -> [Node 3] (Label: 'Override Column Dropdowns')
    • [StatusNormalizationView] -> [POST /reprocess] -> [Node 5] (Label: 'Override Status Category')

After creating all elements, call zoom_to_fit to display the full architecture clearly!
\