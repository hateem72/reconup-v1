# Flowchart Generation Prompt: Central Shared Memory Bus

## Core Concept Overview

In an enterprise Multi-Agent AI system, nodes do not pass complex individual variables to each other. Instead, a **Central Shared Memory Bus** acts as the single source of truth connecting all 7 pipeline stages. 

Each node reads necessary context from this central memory, enriches it with new insights, and passes the updated state forward seamlessly.

---

## High-Level Visual Flowchart Prompt

Generate a clean, visually striking architecture diagram illustrating the **Central Shared Memory Bus**. The diagram should feature the Shared Memory Bus as a prominent gold central spine, with all 7 nodes connected horizontally.

---

### Central Memory Bus Lifecycle (1-Line Summary per Node)

| Stage | Node Name | Data Read | Central Memory Enrichment |
| :--- | :--- | :--- | :--- |
| **0** | **Batch Upload** | User Files | Initializes `Batch ID` & Raw File Buffers |
| **1** | **Ingest & Profiling** | Raw Bytes | Adds `Raw Datasets`, `Sheet Profiles` & `Headers` |
| **1.5** | **Sub-Tab Filter** | All Sheets | Partitions into `Retained` vs. `Dropped` Sub-Tabs |
| **2** | **AI Schema Mapping** | Retained Sheets | Adds `Column Mappings` & `Quality Guardrails` |
| **3** | **Status Normalization** | Mapped Data | Adds `Normalized Records` (Standard Statuses) |
| **4** | **Integrity Audit** | Normalized Data | Adds `Detected Anomalies` & `Proposed Rules` |
| **5** | **Reconciliation Engine** | Standardized Data | Adds `Line-Item Match Matrix` & `Net Payouts` |
| **6** | **Exception Governance** | Discrepancies | Adds `Exception Queue` & `Human Action States` |
| **7** | **Executive Report** | Full History | Adds `Final Report`, `Match Rate %` & `Audit Trail` |

---

### Architecture Diagram Structure

```
                  ┌─────────────────────────────────────────┐
                  │    User Interface & Human Overrides    │
                  └───────────────▲─────▲─────▲─────────────┘
                                  │     │     │ (Real-Time Overrides)
┌─────────────────────────────────┴─────┴─────┴────────────────────────────────┐
│                   CENTRAL SHARED MEMORY BUS (Single Source of Truth)        │
└───────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────┘
        │              │              │              │              │
    ┌───▼───┐      ┌───▼───┐      ┌───▼───┐      ┌───▼───┐      ┌───▼───┐
    │Node 1 │ ───► │Node 2 │ ───► │Node 3 │ ───► │Node 4 │ ───► │Node 5 │ ───► Nodes 6 & 7
    │Ingest │      │Mapping│      │Status │      │Audit  │      │Math   │
    └───────┘      └───────┘      └───────┘      └───────┘      └───────┘
```

---

## Visual Styling Specification

- **Central Shared Memory Bus**: Gold / Amber (`#F59E0B`) — *Central visual focus*
- **Pipeline Stage Nodes**: Deep Blue (`#1E3A8A`) to Emerald Green (`#059669`)
- **Human Override Loops**: Cyan / Blue (`#0284C7`)
- **Key Callout**: `🧠 Single Source of Truth: All 7 agents read & enrich one shared memory.`
