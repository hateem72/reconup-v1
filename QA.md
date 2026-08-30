# Settlement Q&A Engine — Backend Data Flow

## System Overview

The **Settlement Q&A Engine** is a backend service that converts natural language user questions into safe, read-only SQLite queries to retrieve empirical financial facts without manual arithmetic or number hallucination.

---

## Backend Data Flow Diagram

```
                 ┌──────────────────────────────────────────────┐
                 │ User Natural Language Question + Batch ID     │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │ 1. Text-to-SQL Query Generation (Local LLM)   │
                 │    • Schema: orders, payments, rec_results   │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │ 2. Security Check & 6s Timeout Guard         │
                 │    • Enforces SELECT / WITH only             │
                 │    • Rejects DROP / DELETE / UPDATE / ALTER  │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │ 3. SQLite Database Query Execution           │
                 │    • Evaluates SQL query over active batch   │
                 └──────────────────────┬───────────────────────┘
                                        │
                      ┌─────────────────┴─────────────────┐
                      │                                   │
             (If rows returned)                         (If 0 rows / Order ID search)
                      │                                   │
                      ▼                                   ▼
          ┌──────────────────────┐            ┌──────────────────────┐
          │ Retrieved DB Rows    │            │ Multi-Table Fuzzy    │
          │ (Exact Match Facts)  │            │ Fallback Search      │
          └───────────┬──────────┘            └───────────┬──────────┘
                      │                                   │
                      └─────────────────┬─────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │ 4. Executive Answer Synthesis (Local LLM)    │
                 │    • Formats INR (₹) monetary figures        │
                 │    • Direct, crisp markdown tables & facts   │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │ Final JSON API Response + Backend Debug Query│
                 └──────────────────────────────────────────────┘
```

---

## Step-by-Step Data Flow

### 1. Request Intake
- Backend receives natural language question `query` and active `batch_id`.

### 2. Text-to-SQL Query Generation
- Local LLM (`qwen2.5:3b`) inspects database table schemas (`orders`, `payments`, `reconciliation_results`, `exceptions`, `reports`) and generates a SQLite `SELECT` query.

### 3. Security Validation & Timeout Safeguard
- **Read-Only Filter**: Rejects queries containing data-modifying SQL statements (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`).
- **6s Hard Timeout**: Executes query with a thread timeout to ensure zero backend hanging.

### 4. SQLite Execution & Fuzzy Search Fallback
- Executes the `SELECT` query against the SQLite database.
- If exact SQL returns 0 rows or if a partial Order ID is searched, automatically triggers a fuzzy `LEFT JOIN` search across `orders`, `payments`, and `reconciliation_results`.

### 5. Executive Answer Synthesis & Payload Output
- LLM synthesizes retrieved database rows into a direct, fact-grounded answer in INR (₹).
- Returns JSON payload containing: `answer`, `sql_query`, `sql_executed_safely`, and `retrieved_facts`.
