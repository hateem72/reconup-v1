# Flowchart Generation Prompt: Node 1.5 — AI Sub-Tab Relevance Filtering

## Overview & Purpose

- **Stage Name**: `Node 1.5: AI Sub-Tab Relevance Filtering`
- **Core Purpose**: Multi-sheet e-commerce workbooks frequently contain non-essential sub-tabs (like Advertisement Costs, Seller Notes, FAQs, Summary Charts, Tax Guides) alongside core transaction sheets. Node 1.5 uses Artificial Intelligence to analyze every sub-tab and determine whether it is **REQUIRED** for line-item order reconciliation or **NOT REQUIRED** (dropped to streamline processing).
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 1.5: AI Sub-Tab Relevance Filtering**. The diagram should illustrate how raw extracted sub-tabs are evaluated by AI, partitioned into retained vs. dropped sheets, and presented to the user with human override controls.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives all extracted sub-tabs and raw sheet datasets from Node 1.
- **Goal**: Filter out non-financial or summary sub-tabs so downstream AI agents only analyze essential transaction data.

#### 2. Sub-Tab Context Extraction
- **Action**: Extracts metadata and sample rows for each sub-tab:
  - Sub-tab title & declared role (e.g. `Order Payments`, `Ads Cost`, `Returns`).
  - Sheet dimensions (total rows & columns).
  - Column header list & top 2 sample data rows.

#### 3. AI Semantic Relevance Evaluation
- **Processing**: The AI evaluates the structure and contents of each sub-tab:
  - Checks if the sheet contains line-item order numbers, transaction amounts, SKUs, or settlement lines.
  - Checks if the sheet is merely a summary table, advertisement fee log, or informational guide.
- **AI Verdict Assignment**:
  - **REQUIRED**: Sub-tab contains essential line-item order or payment transaction data.
  - **NOT REQUIRED**: Sub-tab is an auxiliary, summary, or non-transactional sheet.
- **Output**: Each sub-tab receives a verdict (`REQUIRED` vs `NOT REQUIRED`) accompanied by a clear, human-readable AI rationale.

#### 4. Sub-Tab Partitioning
- **Action**: Partitions datasets into two pools:
  - **Retained Datasets**: Passed forward for AI column mapping.
  - **Dropped Datasets**: Archived with rationale logged for user reference.

#### 5. Human Review & Override Controls (User Interface)
- **UI Interaction**: Displays a visual summary of retained vs. dropped sub-tabs with AI rationale callouts.
- **Human Control**: Users can toggle any dropped sheet back to `REQUIRED` (or vice-versa) before continuing.
- **Reprocessing**: Any manual toggle updates the pipeline execution path dynamically.

#### 6. Output & Data Handoff
- **Output**: Filtered list of essential transaction sub-tabs (`retained_datasets`).
- **Data Handoff**: Passes retained datasets forward to **Node 2 (AI Schema Mapping)**.

---

## Diagram Styling & Visual Specs

- **Node Intake**: Deep Blue (`#1E3A8A`)
- **Sub-Tab Context Extraction**: Cyan / Teal (`#0D9488`)
- **AI Relevance Classifier**: Orange / Red (`#EA580C`)
- **Retained Sub-Tabs Path**: Emerald Green (`#059669`)
- **Dropped Sub-Tabs Path**: Gray / Slate (`#64748B`)
- **Human Review Controls**: Gold / Amber (`#D97706`)
- **Data Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **🧠 Smart AI Filtering**: Automatically identifies and drops non-essential sheets (Ads, FAQs, Summaries).
- **📝 Clear AI Rationale**: Explains exactly why each sub-tab was kept or dropped.
- **👤 Human Override**: Provides instant visual toggles for users to retain any sheet manually.
- **⚡ Noise Reduction**: Prevents downstream AI nodes from wasting time on non-transactional data.
