# Flowchart Generation Prompt: Node 4 — AI Co-Dependent Status Integrity & Pattern Audit

## Overview & Purpose

- **Stage Name**: `Node 4: AI Co-Dependent Status Integrity & Dynamic Pattern Audit`
- **Core Purpose**: E-commerce spreadsheets (from Meesho, Amazon, Flipkart, etc.) frequently split order status information across multiple **co-dependent columns** (e.g. `Status` and `Returned`, `Live Order Status` and `Return Reason`). Node 4 uses AI intelligence to evaluate co-dependent status columns, impute missing primary statuses from adjacent row fields, and dynamically classify non-order settlement lines into fee deductions (Ads, Recoveries, Commission) vs compensation credits (Claims, Waivers).
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 4: AI Co-Dependent Status Integrity & Dynamic Pattern Audit**. The diagram should illustrate how raw order data and payment settlement events are evaluated by AI across co-dependent status columns, repaired for 100% status coverage, classified into deductions vs. claims, and prepared for line-item reconciliation.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives normalized canonical order records and payment settlement event lines from Node 3 + Active Rule Registry.
- **Goal**: Ensure 100% status completeness and separate non-order fee lines so line-item reconciliation (Node 5) achieves maximum accuracy.

#### 2. AI Co-Dependent Status Integrity & Repair (Master Orders)
- **The Challenge**: In many e-commerce exports, the main `Status` column is blank or null for returned/RTO items, while an adjacent co-dependent column (e.g. `Returned`, `Return Reason`, `Credit Type`) contains the return details.
- **AI Processing**:
  - Scans each order record to inspect primary status fields alongside adjacent co-dependent columns.
  - Dynamically synthesizes the true order lifecycle status (e.g., if `Status` is blank but `Returned` is `"Yes"` / `"Returned"`, imputes status as `Return / RTO`).
- **Outcome**: 100% Status Coverage across all order manifest records with zero missing status gaps.

#### 3. Payment Settlement Event Classification (Deductions vs. Claims vs. Orders)
- **The Challenge**: Payment reports contain order payouts mixed together with marketplace ad costs, penalties, recoveries, and claim payouts.
- **AI Processing**:
  - Analyzes each payment settlement event line dynamically based on financial sign (+/-) and semantic text.
  - Classifies event lines into:
    - **Order Settlement Lines**: Actual payouts for order fulfillment.
    - **Fee Deductions**: Marketplace charges, Ad costs, Logistics recoveries, TCS/TDS penalties.
    - **Compensation / Claims**: Reimbursements, lost shipment claims, and fee waivers.
- **Outcome**: Non-order fee lines are separated so they do not trigger false "missing payment" errors in Node 5.

#### 4. Automated Pattern Detection & Candidate Rule Proposals
- **Processing**: Unrecognized deduction patterns are evaluated by AI to determine financial effect:
  - Formulates candidate rule definitions (e.g. Pattern: `"Return Assurance Fee"`, Category: `Unknown Deduction`, Effect: `SUBTRACT`).
- **Outcome**: Prepares proposed rules ready for one-click human approval in the Governance Queue.

#### 5. Output & Data Handoff
- **Output**: Audited datasets with 100% status coverage, classified payment lines, and pattern risk tags.
- **Data Handoff**: Passes clean audited datasets forward to **Node 5 (Deterministic Reconciliation Engine)**.

---

## Diagram Styling & Visual Specs

- **Node Intake & Inputs**: Deep Blue (`#1E3A8A`)
- **Co-Dependent Status Repair**: Cyan / Teal (`#0D9488`)
- **AI Pattern & Fee Classification**: Orange / Red (`#EA580C`)
- **Non-Order Fee Deductions**: Crimson / Red (`#DC2626`)
- **Compensation & Claims**: Emerald Green (`#059669`)
- **Human Rule Controls**: Gold / Amber (`#D97706`)
- **Data Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **🔗 Co-Dependent Column Repair**: AI evaluates adjacent columns (e.g. `Status` + `Returned`) to repair missing status data dynamically.
- **🎯 100% Status Coverage**: Eliminates status gaps before matching to guarantee reconciliation accuracy.
- **✂️ Fee Line Separation**: Isolates marketplace ad fees and recoveries from order payout lines.
- **💡 Smart Rule Proposals**: AI automatically drafts new rules for unrecognized charge patterns.
