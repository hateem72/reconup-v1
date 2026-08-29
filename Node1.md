# Flowchart Generation Prompt: Node 1 — Multi-File Ingest & Data Profiling

## Overview & Purpose

- **Stage Name**: `Node 1: Multi-File Ingest & Data Profiling`
- **Core Purpose**: Ingests multi-file e-commerce financial workbooks (Excel, CSV, ZIP archives containing Order Manifests and Payment Reports), automatically extracts sub-tabs, finds the true table header row (filtering out top banner text/disclaimers), computes sheet statistics, and streams live processing updates to the user.
- **Design Philosophy**: High-level conceptual data flow for presentation diagrams. Free of code syntax, file paths, or implementation clutter.

---

## High-Level Flowchart Prompt

Generate a clean, color-coded presentation flowchart for **Node 1: Ingest & Data Profiling**. The diagram should illustrate how raw files move from initial user upload through smart header discovery, statistical profiling, and role assignment.

---

### Step-by-Step Data Flow & Functioning

#### 1. File Reception & Ultra-Fast Intake
- **Input**: User uploads Order Manifest files and Payment Settlement Reports (`.xlsx`, `.csv`, `.zip`).
- **Processing**: The system receives the files in memory and acknowledges the upload instantly (<10ms response time) to keep the user interface responsive.
- **Real-Time Notification**: Pushes a live "Ingestion Started" update to the user's execution terminal.

#### 2. Multi-Format File Unpacking & Extraction
- **Format Branching**:
  - **ZIP Archives**: Unpacks files in memory and processes included spreadsheets.
  - **CSV Files**: Detects column delimiters (commas or tabs) and parses raw text into tabular data.
  - **Excel Workbooks**: Discovers all individual sub-tabs and sheets inside the workbook.
- **Output**: A list of raw extracted sub-tabs ready for inspection.

#### 3. Smart True Header Row Discovery
- **The Challenge**: E-commerce reports frequently contain title banners, metadata, or blank rows at the top before the actual table headers appear.
- **Processing**:
  - Scans the top 15 rows of each sheet.
  - Evaluates row contents using a domain scoring system: rewards financial keywords (Order ID, SKU, Payout, Date), penalizes single letters and formulas.
  - Identifies the exact row index where the actual table headers begin.
- **Output**: Clean dataset starting directly from the true header row, with top metadata skipped.

#### 4. Statistical & Semantic Data Profiling
- **Sheet Dimension Check**: Counts total data rows and total columns per sheet.
- **Data Quality Inspection**: Measures missing/null value percentages and uniqueness ratios across columns.
- **Automatic Type Classification**: Scans sample row values using smart pattern matching:
  - *Numeric Columns*: Detects prices, fees, and quantities.
  - *Date Columns*: Detects order dates and settlement timestamps.
  - *Identifier Columns*: Detects Order IDs, SKUs, and Transaction IDs.

#### 5. Automated Sheet Role Classification
- **Processing**: Evaluates discovered column names against e-commerce domain keywords.
- **Role Assignment**:
  - **Payment Settlement Report**: Contains payout, settlement, bank, or fee keywords.
  - **Master Order Manifest**: Contains order placement, customer, or shipping keywords.

#### 6. Ingest Completion & Data Handoff
- **Output**: Structured raw datasets with exact column headers, dimensions, type profiles, and assigned roles.
- **Real-Time Status**: Pushes a "Node 1 Complete" notification to the live user dashboard.
- **Data Handoff**: Passes profiled datasets to **Node 1.5 (Sub-Tab Filtering)**.

---

## Diagram Styling & Visual Specs

- **User Action & Upload Layer**: Deep Blue (`#1E3A8A`)
- **File Unpacking & Extraction**: Cyan / Teal (`#0D9488`)
- **Smart Header Discovery**: Dark Yellow / Amber (`#D97706`)
- **Statistical Profiler**: Emerald Green (`#059669`)
- **Node Output & Handoff**: Purple (`#7C3AED`)

---

## Key Presentation Highlights

- **⚡ Instant Intake**: Immediate UI response (<10ms) while ingestion runs smoothly in the background.
- **🔍 Smart Header Detection**: Automatically ignores top metadata banners, disclaimers, and empty rows.
- **📊 Automatic Profiling**: Detects column data types (Numbers, Dates, Identifiers) and data cleanliness instantly.
