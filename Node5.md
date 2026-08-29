# Flowchart Generation Prompt: Node 5 — Deterministic Settlement Reconciliation Engine

## Overview & Purpose

- **Stage Name**: `Node 5: Deterministic Settlement Reconciliation Engine`
- **Core Purpose**: The core mathematical engine of the platform. Performs 100% deterministic, line-item financial reconciliation between Order Manifests and Payment Settlement Reports (Zero AI — Pure Mathematics) to identify exact matches, overpayments, underpayments, and unsettled orders.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 5: Deterministic Settlement Reconciliation Engine**. The diagram should illustrate how standardized order records and payment settlement lines are indexed, matched line-by-line using mathematical rules, classified into match states, and stored for financial audit.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives standardized canonical orders, canonical payments, and column definitions from Node 4.
- **Badge**: `100% DETERMINISTIC ENGINE — ZERO AI — PURE MATHEMATICS`.
- **Goal**: Perform exact line-item financial matching between order expectations and actual bank/marketplace payouts.

#### 2. Canonical Data Normalization & Formatting
- **Action**: Maps processed raw rows into clean Order objects and Payment objects:
  - *Order Object*: `Order ID`, `SKU`, `Quantity`, `Status`, `Order Date`.
  - *Payment Object*: `Order ID`, `Disbursed Amount (₹)`, `Status`, `Payment Date`.

#### 3. High-Speed Indexing
- **Action**: Builds a high-speed memory lookup index keyed on unique **Order ID**.
- **Benefit**: Enables sub-millisecond line-item matching across tens of thousands of records.

#### 4. Deterministic Line-Item Matching Algorithm
- **Processing**: Iterates every order record and queries the payment index by Order ID.
- **Match State Classification Rules**:
  - **MATCHED**: Order exists AND payment exists, and payout amount matches expected amount within ₹0.01 tolerance.
  - **OVERPAID**: Payment amount received exceeds the expected order settlement amount.
  - **UNDERPAID**: Payment amount received is less than expected (shortfall/over-deduction).
  - **UNSETTLED**: Order manifest exists as delivered, but zero payment has been disbursed in the current cycle.
  - **GHOST PAYMENT**: Payment disbursement received, but no matching order manifest exists in records.

#### 5. Financial Payout & Summary Aggregation
- **Action**: Aggregates batch-wide financial totals:
  - Total Settled Amount (₹)
  - Total Unsettled Amount (₹)
  - Net Payout (₹)
  - Reconciliation Match Rate (%)
  - Matched vs. Unmatched Record Counts

#### 6. Database Audit Persistence
- **Action**: Stores canonical orders, payment lines, and match results into the secure local database for audit trail compliance.

#### 7. Output & Data Handoff
- **Output**: Full reconciliation matrix with match badges and financial summary statistics.
- **Data Handoff**: Passes reconciliation matrix forward to **Node 6 (Exception Governance Queue & AI Q&A)**.

---

## Diagram Styling & Visual Specs

- **Node Intake & Inputs**: Deep Blue (`#1E3A8A`)
- **Deterministic Math Engine**: Emerald Green (`#15803D`) — *Highlights 100% Math/No AI*
- **Indexing & Lookups**: Cyan / Teal (`#0D9488`)
- **Match State Badges**:
  - *Matched*: Bright Green (`#16A34A`)
  - *Overpaid / Underpaid*: Amber (`#D97706`)
  - *Unsettled*: Rose / Red (`#E11D48`)
  - *Ghost Payment*: Purple (`#9333EA`)
- **Database Persistence**: Dark Gray (`#374151`)
- **Data Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **🧮 100% Deterministic Engine**: Pure mathematical accuracy with zero AI guessing or hallucination.
- **⚡ Sub-Millisecond Matching**: High-speed indexing reconciles 50,000 records in seconds.
- **🎯 5 Match Classifications**: Categorizes orders into Matched, Overpaid, Underpaid, Unsettled, and Ghost Payments.
- **🔒 Audited Persistence**: All reconciliation records are saved to the database for accounting compliance.
