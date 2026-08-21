import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class BatchModel(Base):
    __tablename__ = "batches"

    id = Column(String, primary_key=True, index=True) # e.g. batch_123
    batch_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="PENDING")
    source_filename = Column(String, default="")
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    processing_time_ms = Column(Float, default=0.0)

    reconciliation_results = relationship("ReconciliationResultModel", back_populates="batch", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionModel", back_populates="batch", cascade="all, delete-orphan")
    agent_decisions = relationship("AgentDecisionModel", back_populates="batch", cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="batch", cascade="all, delete-orphan")


class ReconciliationResultModel(Base):
    __tablename__ = "reconciliation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String, ForeignKey("batches.id"), index=True)
    order_id = Column(String, index=True)
    match_status = Column(String, index=True) # MATCHED, MISSING_PAYMENT, MISSING_ORDER, etc.
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
    exception_type = Column(String, index=True) # UNKNOWN_DEDUCTION, MISSING_PAYMENT, AMOUNT_MISMATCH, etc.
    raw_status = Column(String, default="")
    amount = Column(Float, default=0.0)
    description = Column(Text, default="")
    agent_analysis = Column(Text, default="")
    confidence = Column(Float, default=0.0)
    status = Column(String, default="PENDING", index=True) # PENDING, APPROVED, REJECTED, RESOLVED
    human_decision = Column(String, default="")
    human_note = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    batch = relationship("BatchModel", back_populates="exceptions")


class RuleRegistryModel(Base):
    __tablename__ = "rule_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern = Column(String, unique=True, index=True) # e.g. "return assurance fee"
    normalized_category = Column(String, default="")
    financial_effect = Column(String, default="SUBTRACT") # ADD, SUBTRACT, NEUTRAL
    amount_behavior = Column(String, default="DEDUCTION") # REVENUE, DEDUCTION, PENALTY, CREDIT, ZERO_AMOUNT
    applies_to = Column(String, default="ALL") # DELIVERED, RETURN, ALL
    confidence = Column(Float, default=1.0)
    created_by = Column(String, default="human") # system, human, agent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    active = Column(Boolean, default=True, index=True)


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
