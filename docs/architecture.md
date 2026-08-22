# Platform-Agnostic AI Finance Controller Architecture

## 1. Overview
The Platform-Agnostic AI Finance Controller is a multi-source reconciliation, profit intelligence, and automated governance platform built using FastAPI, LangGraph, and Local Ollama LLM (`qwen2.5:3b`).

---

## 2. Core Architectural Separation
- **AI Reasoning & Decision Layer**: Sub-tab relevance classification, schema header mapping, status categorization, ambiguity investigation, exception explanation, and natural language Q&A routing.
- **Deterministic Data Processing Layer**: Header profiling, data validation, SQL persistence, date/numeric parsing, window filtering.
- **Financial Truth Layer**: Deterministic P&L, multi-event payout aggregation per order ID, 3-way order ↔ payment matching, unit cost calculation.

---

## 3. Modular Agent Sub-Package Architecture

```text
backend/app/agents/
├── core/                               # Core Infrastructure
│   ├── llm_factory.py                 # Local Ollama LLM Factory (qwen2.5:3b)
│   ├── state.py                       # LangGraph Pipeline State Schemas
│   ├── prompts.py                     # Centralized System & Agent Prompts
│   └── tools.py                       # LangChain Order/Payment Query Tools
│
├── specialized/                       # Autonomous AI Reasoning Agents
│   ├── sheet_relevance_agent.py       # SheetRelevanceAgent (Sub-tab Relevance Classifier)
│   ├── column_mapping_agent.py        # ColumnMappingAgent (LLM Header Mapper)
│   ├── status_normalization_agent.py  # StatusNormalizationAgent (Lifecycle Categorizer)
│   └── pattern_detection_agent.py     # PatternDetectionAgent (Integrity Repair Audit)
│
├── nodes/                             # Pipeline Graph Execution Step Nodes
│   ├── ingest_node.py                 # Node 1: Ingest & Exact Header Profiling
│   ├── relevance_node.py              # Node 1.5: AI Sheet Relevance Filtering
│   ├── mapping_node.py                # Node 2: Mapping & Structural Guardrails
│   ├── normalization_node.py          # Node 3: Canonical Model Normalization
│   ├── integrity_node.py              # Node 4: Status Integrity Repair Audit
│   ├── reconciliation_node.py         # Node 5: Deterministic Reconciliation Engine
│   ├── financial_calculation_node.py  # Node 6: Profit & Loss Calculation
│   ├── exception_analysis_node.py     # Node 7: Exception Governance Analysis
│   └── report_node.py                 # Node 8: Executive Report Generator
│
├── finance_graph.py                   # LangGraph State Machine Workflow Graph
└── nodes.py                           # Central Backward-Compatible Re-Exporter Registry
```

---

## 4. Canonical Schemas

### CanonicalOrder
- `order_id`: Primary order identifier (e.g. `ORD-1001`, `Sub Order No`)
- `sku`: Product SKU ID
- `product_name`: Title or product description
- `quantity`: Dispatched quantity
- `status`: Normalized lifecycle status (`Delivered`, `Return`, `RTO`, `Cancelled`, `Shipped`)
- `dispatch_date`: Date dispatched
- `order_date`: Order placement date
- `source_platform`: Platform name (`Meesho/Generic`)
- `source_file`, `source_sheet`, `source_row`: Complete data line traceability

### CanonicalPayment
- `transaction_id`: Unique payment line ID
- `order_id`: Target order ID
- `sku`: Product SKU ID
- `status`: Payment event status
- `quantity`: Item quantity
- `payment_date`: Settlement date
- `settlement_amount`: Net settled amount (+/- float)
- `transaction_type`: SETTLEMENT, DEDUCTION, FEE, CREDIT, ADJUSTMENT
- `adjustment_reason`: Raw description (e.g., Return Assurance Charge, Platform Fee)
- `source_file`, `source_sheet`, `source_row`: Complete data line traceability

---

## 5. Deterministic Profit Formula
$$\text{Final Profit} = (\text{Delivered Sales} + \text{Cancelled Sales}) - \text{Return Penalty} - \text{Total Cost} + \text{Claims} - \text{Affiliate Fees} + \text{Exchange}$$
$$\text{Total Cost} = (\text{Delivered Count} + \text{Cancelled Count}) \times (\text{Product Cost Price} + \text{Packaging Cost})$$
