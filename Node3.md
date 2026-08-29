# Flowchart Generation Prompt: Node 3 — Order Status Normalization

## Overview & Purpose

- **Stage Name**: `Node 3: Order Status Normalization`
- **Core Purpose**: Standardizes hundreds of raw, platform-specific order status text descriptions (e.g. *"Delivered to Customer"*, *"RTO Initiated"*, *"Return Assurance Fee"*, *"Cancelled by Buyer"*) across all files into standard business categories using Artificial Intelligence. Employs bulk status deduplication to process tens of thousands of rows in a single AI call.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 3: Order Status Normalization**. The diagram should illustrate how raw status text across thousands of rows is extracted, deduplicated for bulk efficiency, classified by AI into standard categories, and applied back across the full dataset.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives datasets with standardized column definitions from Node 2.
- **Goal**: Convert all raw order statuses into standard business buckets required for accurate financial reconciliation.

#### 2. Raw Status Extraction
- **Action**: Locates the mapped status column in each dataset and extracts raw text descriptions across all rows.
- **Example Raw Input**: `["Delivered", "Delivered to Customer", "Return Assurance Fee", "RTO Initiated", "Cancelled by Buyer", "Claim Approved"]`.

#### 3. Smart Deduplication Optimization
- **The Efficiency Challenge**: Processing 50,000 individual spreadsheet rows through AI one-by-one is slow and costly.
- **Processing**:
  - Extracts only the **unique status values** present in the file set (e.g. 50,000 rows contain only 6 unique status strings).
  - Bundles the unique status strings into a single bulk request.
- **Benefit**: Reduces 50,000 potential AI calls down to **1 single bulk AI operation** (up to 99.9% faster).

#### 4. AI Bulk Status Classification
- **Processing**: The AI analyzes each unique status string conceptually and categorizes it into a standard business bucket:
  - **Delivered**: Successful order fulfillment and customer delivery.
  - **Return / RTO**: Customer return or Return-To-Origin shipment.
  - **Cancelled**: Order cancelled prior to delivery.
  - **Claim**: Lost/damaged shipment warranty or claim payout.
  - **Exchange**: Item replacement or product exchange transaction.
  - **Unknown Deduction**: Unrecognized fee or charge requiring further integrity audit.
- **Output**: A standardized lookup dictionary mapping each raw status text to its standard category.

#### 5. Bulk Row Mapping & Dataset Normalization
- **Processing**: Applies the AI classification lookup dictionary back across all 50,000 original spreadsheet rows in parallel.
- **Output**: Fully normalized dataset where every record now contains a clean `canonical_status` field.

#### 6. Human Review & Correction Controls (User Interface)
- **UI Interaction**: Displays raw statuses alongside their AI-classified standard categories in an intuitive dashboard table.
- **Human Correction**: Users can adjust any category dropdown if a specific business rule requires a custom classification.
- **Reprocessing**: Any manual adjustment updates the dataset instantly for downstream processing.

#### 7. Output & Data Handoff
- **Output**: Datasets with normalized, standard status categories on every order record.
- **Data Handoff**: Passes normalized datasets forward to **Node 4 (Pattern Detection & Integrity Audit)**.

---

## Diagram Styling & Visual Specs

- **Node Intake & Input**: Deep Blue (`#1E3A8A`)
- **Deduplication Optimization**: Cyan / Teal (`#0D9488`)
- **AI Bulk Classification**: Orange / Red (`#EA580C`)
- **Normalized Output Dataset**: Emerald Green (`#059669`)
- **Human Correction Controls**: Gold / Amber (`#D97706`)
- **Data Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **⚡ Bulk Efficiency**: Deduplicates 50,000 rows into unique statuses to execute in **1 single AI call**.
- **🎯 Standard Categorization**: Unifies messy platform terminology into standard buckets (Delivered, Return, Cancelled, Claim).
- **🔍 Anomaly Detection**: Automatically flags unrecognized status strings as Unknown Deductions for audit.
- **👤 Human Override**: Provides clear visual controls for users to review and adjust status classifications anytime.
