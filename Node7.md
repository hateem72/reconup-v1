# Flowchart Generation Prompt: Node 7 — Executive Report Generation & Audit Metrics

## Overview & Purpose

- **Stage Name**: `Node 7: Executive Report Generation & Audit Metrics`
- **Core Purpose**: The final stage of the pipeline. Aggregates reconciliation statistics, match rates, net payouts, unresolved financial exposure, throughput, and AI audit trails into executive summary reports and downloadable audit files.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 7: Executive Report Generation & Audit Metrics**. The diagram should illustrate how final batch reconciliation results are synthesized into executive KPIs, persistent database reports, and downloadable audit exports.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives final reconciliation matrix, resolved exception logs, and pipeline execution timers from Node 6.
- **Goal**: Synthesize raw batch data into executive KPIs and formal financial compliance reports.

#### 2. Executive KPI Computation
- **Processing**: Calculates core business metrics:
  - **Match Rate (%)**: Percentage of order records successfully reconciled.
  - **Net Payout (₹)**: Total net money settled and disbursed by platforms.
  - **Unresolved Exposure (₹)**: Total monetary value of unresolved exceptions requiring attention.
  - **Processing Speed**: Processing time in seconds and throughput in records per second.
  - **AI Confidence Average**: Average confidence score across all AI decisions in the batch.

#### 3. Complete Audit Trail Assembly
- **Processing**: Consolidates the complete audit trail:
  - Records every AI agent decision (sheet filtering, column mapping, status normalization, pattern detection).
  - Logs all human overrides and exception resolution actions (Accept / Reject / Escalate).

#### 4. Persistent Database Report Storage
- **Action**: Saves the final batch report record into the secure local database for long-term auditing and historical lookup.

#### 5. Report Export & Dashboard Presentation (User Interface)
- **UI Presentation**: Displays an Executive Summary Dashboard featuring interactive charts, match rate gauges, and financial summaries.
- **Download Capabilities**: Enables one-click report downloads in structured JSON / Excel format for accounting and ERP integration.

#### 6. Pipeline Completion
- **Action**: Emits a `PIPELINE_COMPLETE` status notification to the frontend.
- **Outcome**: The entire multi-file reconciliation cycle is complete and ready for the next batch.

---

## Diagram Styling & Visual Specs

- **Node Intake & Inputs**: Deep Blue (`#1E3A8A`)
- **KPI Calculation Engine**: Emerald Green (`#059669`)
- **Audit Trail Consolidation**: Cyan / Teal (`#0D9488`)
- **Database Storage**: Dark Gray (`#374151`)
- **Executive Dashboard UI**: Bright Blue (`#0284C7`)
- **Download / Export Engine**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **📈 Executive KPIs**: Instantly shows Match Rate (%), Net Payout (₹), and Unresolved Exposure (₹).
- **⏱️ Processing Speed**: Displays total batch processing time and records-per-second throughput.
- **📜 Complete Audit Trail**: Tracks every AI agent decision and human override for full compliance.
- **📥 One-Click Export**: Downloads final audited reports ready for ERP or accounting integration.
