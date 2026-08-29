# Flowchart Generation Prompt: Node 4 — Pattern Detection & Integrity Audit

## Overview & Purpose

- **Stage Name**: `Node 4: Pattern Detection & Integrity Audit`
- **Core Purpose**: Audits normalized e-commerce data against registered business rules to identify unknown, anomalous, or suspicious deduction patterns (e.g. *"Return Assurance Fee"*, *"Affiliate Charges"*, *"Unrecognized Penalty"*) that are not registered in the system. Surfaces candidate rules for human governance approval.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 4: Pattern Detection & Integrity Audit**. The diagram should illustrate how normalized order data is scanned against known business rules, evaluated by AI for unknown deduction patterns, classified into risk buckets, and presented with proposed rule additions.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives normalized datasets from Node 3 + Active Known Business Rule Registry.
- **Goal**: Detect hidden fees, unauthorized charges, or new deduction types before financial settlement reconciliation.

#### 2. Known Business Rule Matching
- **Processing**: Compares all raw status and description strings against pre-registered, human-approved deduction rules (e.g. standard Return Fees, Shipping Deductions, Commission Fees).
- **Match Branching**:
  - **Recognized Rule**: Deduction type is already known and registered → tagged as `KNOWN DEDUCTION`.
  - **Unrecognized Pattern**: Description does not match any registered rule → routed to AI Pattern Detection.

#### 3. AI Pattern Detection & Anomaly Analysis
- **Processing**: Unrecognized deduction descriptions are analyzed conceptually by Artificial Intelligence.
- **AI Classification Buckets**:
  - **KNOWN DEDUCTION**: Recognized as standard business fee.
  - **UNKNOWN DEDUCTION**: New fee pattern surfaced for user awareness and review.
  - **SUSPICIOUS ANOMALY**: Unexpected penalty or unusual charge requiring audit.

#### 4. Automated Rule Proposal Generation
- **Processing**: For newly discovered deduction patterns, the AI automatically formulates a candidate rule definition:
  - *Pattern Name*: e.g., `"Return Assurance Fee"`.
  - *Target Standard Category*: e.g., `Unknown Deduction` or `Return Fee`.
  - *Financial Impact*: `ADD`, `SUBTRACT`, or `NEUTRAL`.
- **Outcome**: Prepares proposed rules ready for one-click human approval.

#### 5. Pattern Analysis Summary
- **Action**: Aggregates total recognized vs. unrecognized deduction patterns across the batch.
- **Output**: Detailed audit report listing detected anomalies, risk levels, and suggested rules.

#### 6. Human Governance & Rule Approval Controls (User Interface)
- **UI Interaction**: Displays surfaced anomalies in an interactive Rule Registry dashboard.
- **Human Controls**:
  - **APPROVE RULE**: Adds the proposed rule to the system permanent registry for all future uploads.
  - **REJECT**: Reclassifies the pattern or flags for investigation.

#### 7. Output & Data Handoff
- **Output**: Audited datasets with pattern tags and rule proposals.
- **Data Handoff**: Passes audited datasets forward to **Node 5 (Deterministic Reconciliation Engine)**.

---

## Diagram Styling & Visual Specs

- **Node Intake & Inputs**: Deep Blue (`#1E3A8A`)
- **Known Rule Matching**: Cyan / Teal (`#0D9488`)
- **AI Pattern Detection**: Orange / Red (`#EA580C`)
- **Surfaced Anomalies & Risks**: Crimson / Red (`#DC2626`)
- **Proposed Rule Generator**: Emerald Green (`#059669`)
- **Human Rule Approval Controls**: Gold / Amber (`#D97706`)
- **Data Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **🔍 Anomaly Detection**: Automatically catches unknown or hidden fees not found in standard reports.
- **🤖 AI Pattern Analysis**: Conceptually evaluates unrecognized charges to determine risk levels.
- **💡 Smart Rule Proposals**: AI automatically drafts new rules for user approval.
- **📜 Permanent Learning**: Human-approved rules are saved to handle future uploads automatically.
