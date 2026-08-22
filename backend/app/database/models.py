import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class BatchModel(Base):
    __tablename__ = "batches"

    id = Column(String, primary_key=True, index=True)
    batch_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="PENDING")
    source_filename = Column(String, default="")
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    processing_time_ms = Column(Float, default=0.0)

    files = relationship("FileModel", back_populates="batch", cascade="all, delete-orphan")
    orders = relationship("OrderModel", back_populates="batch", cascade="all, delete-orphan")
    payments = relationship("PaymentModel", back_populates="batch", cascade="all, delete-orphan")
    reconciliation_results = relationship("ReconciliationResultModel", back_populates="batch", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionModel", back_populates="batch", cascade="all, delete-orphan")
    agent_decisions = relationship("AgentDecisionModel", back_populates="batch", cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="batch", cascade="all, delete-orphan")
    audit_events = relationship("AuditEventModel", back_populates="batch", cascade="all, delete-orphan")


class FileModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    filename = Column(String, index=True)
    file_type = Column(String, default="SPREADSHEET")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    batch = relationship("BatchModel", back_populates="files")
    sheets = relationship("SheetModel", back_populates="file", cascade="all, delete-orphan")


class SheetModel(Base):
    __tablename__ = "sheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    sheet_name = Column(String, index=True)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    detected_type = Column(String, default="UNKNOWN") # ORDER, PAYMENT, SUMMARY

    file = relationship("FileModel", back_populates="sheets")


class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    order_id = Column(String, index=True)
    sku = Column(String, index=True, default="")
    product_name = Column(String, default="")
    quantity = Column(Integer, default=1)
    status = Column(String, index=True, default="Unknown")
    dispatch_date = Column(String, default="")
    order_date = Column(String, default="")
    source_file = Column(String, default="")
    source_sheet = Column(String, default="")
    source_row = Column(Integer, default=0)
    raw_data = Column(JSON, default=dict)

    batch = relationship("BatchModel", back_populates="orders")


class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    transaction_id = Column(String, index=True)
    order_id = Column(String, index=True)
    sku = Column(String, default="")
    status = Column(String, default="")
    quantity = Column(Integer, default=1)
    payment_date = Column(String, default="")
    settlement_amount = Column(Float, default=0.0)
    transaction_type = Column(String, default="SETTLEMENT")
    adjustment_reason = Column(String, default="")
    source_file = Column(String, default="")
    source_sheet = Column(String, default="")
    source_row = Column(Integer, default=0)
    raw_data = Column(JSON, default=dict)

    batch = relationship("BatchModel", back_populates="payments")


class ReconciliationResultModel(Base):
    __tablename__ = "reconciliation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    order_id = Column(String, index=True)
    match_status = Column(String, index=True)
    order_status = Column(String, default="")
    payment_status = Column(String, default="")
    payment_amount = Column(Float, default=0.0)
    difference = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    reason = Column(Text, default="")

    batch = relationship("BatchModel", back_populates="reconciliation_results")


class ExceptionModel(Base):
    __tablename__ = "exceptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    record_id = Column(String, index=True)
    order_id = Column(String, index=True)
    exception_type = Column(String, index=True)
    raw_status = Column(String, default="")
    amount = Column(Float, default=0.0)
    description = Column(Text, default="")
    agent_analysis = Column(Text, default="")
    confidence = Column(Float, default=0.0)
    status = Column(String, default="PENDING", index=True)
    human_decision = Column(String, default="")
    human_note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    batch = relationship("BatchModel", back_populates="exceptions")


class RuleRegistryModel(Base):
    __tablename__ = "rule_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern = Column(String, unique=True, index=True)
    normalized_category = Column(String, default="")
    financial_effect = Column(String, default="SUBTRACT")
    amount_behavior = Column(String, default="DEDUCTION")
    applies_to = Column(String, default="ALL")
    confidence = Column(Float, default=1.0)
    created_by = Column(String, default="human")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean, default=True, index=True)


class SkuCostModel(Base):
    __tablename__ = "sku_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, unique=True, index=True)
    cost_price = Column(Float, default=0.0)
    packaging_cost = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


class AgentDecisionModel(Base):
    __tablename__ = "agent_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    exception_id = Column(String, default="", index=True)
    agent_name = Column(String, default="FinanceControllerAgent")
    decision_type = Column(String, default="")
    input_context = Column(JSON, default=dict)
    decision = Column(String, default="")
    confidence = Column(Float, default=0.0)
    reasoning_summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    batch = relationship("BatchModel", back_populates="agent_decisions")


class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    report_type = Column(String, default="PROFIT_AND_RECONCILIATION")
    match_rate = Column(Float, default=0.0)
    resolved_count = Column(Integer, default=0)
    unresolved_count = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    summary_json = Column(JSON, default=dict)
    sku_breakdown_json = Column(JSON, default=dict)

    batch = relationship("BatchModel", back_populates="reports")


class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    event_type = Column(String, index=True) # STAGE_START, AGENT_DECISION, HUMAN_REVIEW, ERROR
    stage_name = Column(String, index=True)
    description = Column(Text, default="")
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    batch = relationship("BatchModel", back_populates="audit_events")
