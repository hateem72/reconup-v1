from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CanonicalOrder(BaseModel):
    order_id: str = Field(description="Unique order ID or sub-order number")
    sku: str = Field(default="", description="Product SKU ID")
    product_name: Optional[str] = Field(default="", description="Product title or description")
    quantity: int = Field(default=1, description="Dispatched unit quantity")
    status: str = Field(default="Unknown", description="Normalized lifecycle status")
    dispatch_date: Optional[str] = Field(default="", description="Order dispatch date")
    order_date: Optional[str] = Field(default="", description="Order placement date")
    source_platform: str = Field(default="Generic", description="Source platform name")
    source_file: str = Field(default="", description="Source spreadsheet filename")
    source_sheet: str = Field(default="", description="Source sheet name")
    source_row: int = Field(default=0, description="Source row index for 100% traceability")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw source dictionary")


class CanonicalPayment(BaseModel):
    transaction_id: str = Field(default="", description="Unique payment event ID")
    order_id: str = Field(description="Target order ID")
    sku: Optional[str] = Field(default="", description="Product SKU ID")
    status: str = Field(default="", description="Payment event status")
    quantity: int = Field(default=1, description="Item quantity")
    payment_date: Optional[str] = Field(default="", description="Settlement timestamp")
    settlement_amount: float = Field(default=0.0, description="Net settlement amount (+/- float)")
    transaction_type: str = Field(default="SETTLEMENT", description="SETTLEMENT, DEDUCTION, FEE, CREDIT, ADJUSTMENT")
    adjustment_reason: Optional[str] = Field(default="", description="Raw reason or fee description")
    fee_amount: float = Field(default=0.0, description="Platform commission or fee")
    deduction_amount: float = Field(default=0.0, description="Deduction penalty amount")
    source_platform: str = Field(default="Generic", description="Source platform name")
    source_file: str = Field(default="", description="Source spreadsheet filename")
    source_sheet: str = Field(default="", description="Source sheet name")
    source_row: int = Field(default=0, description="Source row index")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw source dictionary")


class SettlementWindow(BaseModel):
    order_start_date: Optional[str] = None
    order_end_date: Optional[str] = None
    payment_start_date: Optional[str] = None
    payment_end_date: Optional[str] = None


class ColumnProfile(BaseModel):
    column_name: str
    column_index: int
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    uniqueness_ratio: float
    sample_values: List[Any]
    date_like: bool
    numeric_like: bool
    identifier_like: bool


class SheetProfile(BaseModel):
    sheet_name: str
    sheet_index: int
    row_count: int
    column_count: int
    preview_rows: List[List[Any]]
    candidate_header_rows: List[int]
    column_profiles: List[ColumnProfile]


class ColumnMapping(BaseModel):
    source_column: str
    canonical_field: str
    confidence: float
    rationale: str


class ColumnMappingResult(BaseModel):
    sheet_name: str
    header_row: int
    data_start_row: int
    mappings: Dict[str, ColumnMapping] # canonical_field -> ColumnMapping
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
