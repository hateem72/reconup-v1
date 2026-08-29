# Flowchart Generation Prompt: Node 2 — AI Schema Mapping & Quality Guardrails

## Overview & Purpose

- **Stage Name**: `Node 2: AI Schema Mapping & Quality Guardrails`
- **Core Purpose**: Automatically translates raw, unpredictable column names from any e-commerce platform (Meesho, Amazon, Flipkart, Shopify, custom spreadsheets) into standardized financial fields using Artificial Intelligence. Includes instant memory caching for recurring file layouts and automated data quality guardrails.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 2: AI Schema Mapping & Quality Guardrails**. The diagram should illustrate how raw spreadsheet column headers are processed through layout fingerprinting, instant cache matching, AI semantic translation, quality guardrails, and human review controls.

---

### Step-by-Step Data Flow & Functioning

#### 1. Input Reception
- **Input**: Receives essential sub-tabs retained from Node 1.5.
- **Goal**: Standardize column definitions across all files so the reconciliation engine can read them uniformly.

#### 2. Layout Fingerprinting & Instant Cache Check
- **Fingerprinting**: Generates a unique layout signature based on the file's column structure.
- **Decision Branch**:
  - **PATH A — Cache Hit (Lightning 0s Bypass)**:
    - *Condition*: The system has processed this exact spreadsheet layout before.
    - *Action*: Reuses the previously learned AI column mapping instantly (0-second delay, zero AI API cost).
    - *Outcome*: Skips AI generation and jumps directly to data validation.
  - **PATH B — Cache Miss**:
    - *Condition*: A new or modified file layout is detected.
    - *Action*: Sends column headers and sample data rows to the AI Engine for analysis.

#### 3. AI Semantic Column Translation
- **Processing**: The AI analyzes column headers and sample row values conceptually (e.g. recognizing that `"Sub Order No"`, `"Order ID"`, or `"Reference #"` all mean `Order ID`).
- **Target Standard Fields**:
  - *Order Files*: Maps `Order ID`, `SKU`, `Quantity`, `Status`, and `Order Date`.
  - *Payment Files*: Maps `Order ID`, `SKU`, `Quantity`, `Status`, `Payment Date`, and `Payout Amount`.
- **Output**: A complete mapping matrix linking raw spreadsheet columns to standardized fields, complete with AI confidence scores.

#### 4. Cache Storage for Future Runs
- **Action**: Saves the approved AI mapping matrix into memory with a 24-hour retention period.
- **Benefit**: Future uploads of the same file format will execute instantly with zero latency.

#### 5. Data Quality Guardrails Check
- **Processing**: Runs automated quality rules on the mapped dataset.
- **Validation Criteria**:
  - Verifies that mandatory fields (`Order ID` and `Amount`) are properly identified.
  - Checks for high missing-value percentages in critical columns.
- **Status Assignment**:
  - **VALID**: All mandatory fields identified with high quality.
  - **WARNINGS FOUND**: Missing non-critical fields flagged for user awareness.

#### 6. Human Review & Reprocessing Loop (User Interface)
- **UI Interaction**: Displays mapped columns in an interactive table with AI confidence indicators (`95% Confidence`).
- **Human Controls**: The user can adjust any column dropdown if a correction is needed.
- **Reprocessing**: Saving changes triggers an instant re-run from Node 3 onwards without repeating ingestion or mapping.

#### 7. Output & Data Handoff
- **Output**: Fully mapped datasets with standard field definitions.
- **Data Handoff**: Passes mapped datasets forward to **Node 3 (Status Normalization)**.

---

## Diagram Styling & Visual Specs

- **Node Intake & Pipeline**: Deep Blue (`#1E3A8A`)
- **Instant Cache Lookup**: Gold / Amber (`#F59E0B`) with Lightning Icon (`⚡ 0s Latency`)
- **AI Translation Engine**: Orange / Red (`#EA580C`)
- **Quality Guardrails**: Emerald Green (`#059669`)
- **Human Review Controls**: Cyan / Blue (`#0284C7`)
- **Data Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **⚡ Instant Memory Caching**: Reuses learned mappings for recurring monthly files with 0-second AI delay.
- **🤖 Smart AI Mapping**: Effortlessly understands column names from any platform without rigid rules.
- **🛡️ Quality Guardrails**: Automatically verifies mandatory fields before processing financial data.
- **👤 Human Control**: Users can review, fine-tune, or override any mapping anytime.
