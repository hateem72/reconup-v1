# Flowchart Generation Prompt: Node 6 — Exception Governance Queue & AI Finance Q&A

## Overview & Purpose

- **Stage Name**: `Node 6: Exception Governance Queue & AI Finance Q&A`
- **Core Purpose**: Surfaces financial discrepancies (unmatched orders, shortfalls, ghost payments, unknown fees) into an interactive human governance queue where finance teams can accept, reject, or escalate exceptions. Features an interactive AI Assistant for natural language Q&A grounded directly in database records.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 6: Exception Governance Queue & AI Finance Q&A**. The diagram should illustrate how reconciliation discrepancies are surfaced as exceptions, severity-ranked, presented to finance managers for action, and integrated with an interactive AI Q&A assistant.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives full reconciliation results and matched/unmatched record matrices from Node 5.
- **Goal**: Isolate financial risks and provide governance workflows for human finance teams.

#### 2. Exception Detection & Categorization
- **Processing**: Evaluates all unmatched or discrepant transactions and categorizes them into specific exception types:
  - **MISSING PAYMENT**: Order delivered, but zero payout received from platform.
  - **AMOUNT MISMATCH**: Payout received differs from expected settlement amount.
  - **GHOST PAYMENT**: Money disbursed without a matching order record.
  - **UNKNOWN DEDUCTION**: Unrecognized fee or charge pattern.
  - **STATUS DISCREPANCY**: Order status conflicts between manifest and payment report.

#### 3. Severity Ranking & Financial Impact Calculation
- **Processing**: Calculates the monetary exposure (`financial_impact_inr`) for each exception.
- **Severity Levels**:
  - **HIGH**: Large payout shortfall or missing payment (High financial risk).
  - **MEDIUM**: Minor amount mismatch or status discrepancy.
  - **LOW**: Informational exception or neutral fee variance.

#### 4. Human Governance Queue (User Interface)
- **UI Interaction**: Displays exceptions in an interactive Governance Queue dashboard sorted by severity and impact.
- **Human Action Controls**:
  - **ACCEPT**: Confirm the discrepancy and clear the exception.
  - **REJECT**: Flag as an unauthorized deduction to claim from marketplace.
  - **ESCALATE**: Route for senior audit or finance manager review.

#### 5. Interactive AI Finance Assistant (Q&A Chat)
- **UI Interaction**: Users can type natural language questions into an integrated AI Finance Chat widget (e.g. *"What is the total payout shortfall for June?"* or *"Why was Order ORD-1002 flagged as Underpaid?"*).
- **Processing**: The AI Assistant queries database records directly for empirical facts.
- **Output**: Returns precise, mathematically grounded answers with zero numbers hallucinated.

#### 6. Output & Data Handoff
- **Output**: Resolved and audited exception matrix.
- **Data Handoff**: Passes final batch results forward to **Node 7 (Executive Report Generation)**.

---

## Diagram Styling & Visual Specs

- **Node Intake & Inputs**: Deep Blue (`#1E3A8A`)
- **Exception Detection**: Crimson / Red (`#DC2626`)
- **Severity Badges**:
  - *High*: Red (`#EF4444`)
  - *Medium*: Amber (`#F59E0B`)
  - *Low*: Blue (`#3B82F6`)
- **Human Governance Actions**: Gold / Amber (`#D97706`)
- **AI Finance Q&A Chat**: Purple (`#7C3AED`)
- **Data Handoff**: Emerald Green (`#059669`)

---

## Key Presentation Highlights

- **🚨 Automated Risk Isolation**: Instantly pinpoints shortfalls, ghost payments, and missing money.
- **⚖️ 3-Way Governance Controls**: Finance teams can Accept, Reject, or Escalate any exception.
- **💬 Grounded AI Assistant**: Users can ask natural language questions answered directly from database facts.
- **📊 Impact Ranking**: Prioritizes exceptions by monetary value to focus human audit time efficiently.
