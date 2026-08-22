# Platform-Agnostic AI Finance Controller Architecture

## 1. Overview
The Platform-Agnostic AI Finance Controller is a multi-source reconciliation, profit intelligence, and automated governance platform.

## 2. Core Architectural Separation
- **AI Decision / Interpretation**: Sheet selection, header row detection, column mapping, ambiguity investigation, exception explanation.
- **Data Execution**: Pandas profiling, column validation, SQL writes, date/numeric parsing, window filtering.
- **Financial Truth**: Deterministic P&L, multi-event payment aggregation, order ↔ payment matching, unit cost calculation.

## 3. Canonical Schemas
### CanonicalOrder
- `order_id`: Primary order identifier
- `sku`: Product SKU ID
- `product_name`: Title or product description
- `quantity`: Dispatched quantity
- `status`: Normalized lifecycle status (Delivered, Return, RTO, Cancelled, Shipping)
- `dispatch_date`: Date dispatched
- `order_date`: Order placement date
- `source_platform`: Platform name
- `source_file`: File name
- `source_sheet`: Sheet name
- `source_row`: Source row index

### CanonicalPayment
- `transaction_id`: Unique payment line ID
- `order_id`: Target order ID
- `sku`: SKU ID
- `status`: Payment event status
- `quantity`: Item quantity
- `payment_date`: Settlement date
- `settlement_amount`: Net settled amount (+/- float)
- `transaction_type`: SETTLEMENT, DEDUCTION, FEE, CREDIT, ADJUSTMENT
- `adjustment_reason`: Raw description (e.g. Return Charge, Platform Fee)
- `source_file`, `source_sheet`, `source_row`: Traceability fields

## 4. Deterministic Profit Formula
$$\text{Final Profit} = (\text{Delivered Sales} + \text{Cancelled Sales}) - \text{Return Penalty} - \text{Total Cost} + \text{Claims} - \text{Affiliate Fees} + \text{Exchange}$$
$$\text{Total Cost} = (\text{Delivered Count} + \text{Cancelled Count}) \times (\text{Product Cost Price} + \text{Packaging Cost})$$
