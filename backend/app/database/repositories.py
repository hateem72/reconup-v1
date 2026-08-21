import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import (
    BatchModel,
    ReconciliationResultModel,
    ExceptionModel,
    RuleRegistryModel,
    AgentDecisionModel,
    ReportModel
)

class FinanceRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Batch Operations ──────────────────────────────────────────
    def create_batch(self, batch_id: str, source_filename: str = "", total_records: int = 0) -> BatchModel:
        batch = BatchModel(
            id=batch_id,
            batch_id=batch_id,
            status="UPLOADING",
            source_filename=source_filename,
            total_records=total_records,
            processed_records=0
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_batch(self, batch_id: str) -> Optional[BatchModel]:
        return self.db.query(BatchModel).filter(BatchModel.id == batch_id).first()

    def update_batch_status(
        self,
        batch_id: str,
        status: str,
        processed_records: Optional[int] = None,
        processing_time_ms: Optional[float] = None
    ) -> Optional[BatchModel]:
        batch = self.get_batch(batch_id)
        if batch:
            batch.status = status
            if processed_records is not None:
                batch.processed_records = processed_records
            if processing_time_ms is not None:
                batch.processing_time_ms = processing_time_ms
            self.db.commit()
            self.db.refresh(batch)
        return batch

    # ── Reconciliation Results ─────────────────────────────────────
    def save_reconciliation_results(self, batch_id: str, results: List[Dict[str, Any]]) -> List[ReconciliationResultModel]:
        entities = []
        for r in results:
            item = ReconciliationResultModel(
                batch_id=batch_id,
                order_id=r.get("orderId", ""),
                match_status=r.get("matchStatus", "MATCHED"),
                order_status=r.get("orderSheetStatus", ""),
                payment_status=r.get("paymentStatuses", ""),
                payment_amount=float(r.get("totalPayment", 0.0)),
                difference=float(r.get("difference", 0.0)),
                confidence=float(r.get("confidence", 1.0)),
                reason=r.get("reason", "")
            )
            self.db.add(item)
            entities.append(item)
        self.db.commit()
        return entities

    def get_reconciliation_results(self, batch_id: str) -> List[ReconciliationResultModel]:
        return self.db.query(ReconciliationResultModel).filter(ReconciliationResultModel.batch_id == batch_id).all()

    # ── Exceptions ──────────────────────────────────────────────────
    def save_exceptions(self, batch_id: str, exceptions_data: List[Dict[str, Any]]) -> List[ExceptionModel]:
        entities = []
        for exc in exceptions_data:
            item = ExceptionModel(
                batch_id=batch_id,
                record_id=str(exc.get("record_id", "")),
                order_id=str(exc.get("order_id", "")),
                exception_type=exc.get("exception_type", "UNKNOWN"),
                raw_status=exc.get("raw_status", ""),
                amount=float(exc.get("amount", 0.0)),
                description=exc.get("description", ""),
                agent_analysis=exc.get("agent_analysis", ""),
                confidence=float(exc.get("confidence", 0.0)),
                status=exc.get("status", "PENDING")
            )
            self.db.add(item)
            entities.append(item)
        self.db.commit()
        return entities

    def get_exceptions(self, batch_id: str, status_filter: Optional[str] = None) -> List[ExceptionModel]:
        query = self.db.query(ExceptionModel).filter(ExceptionModel.batch_id == batch_id)
        if status_filter:
            query = query.filter(ExceptionModel.status == status_filter)
        return query.all()

    def get_exception_by_id(self, exception_id: int) -> Optional[ExceptionModel]:
        return self.db.query(ExceptionModel).filter(ExceptionModel.id == exception_id).first()

    def resolve_exception(self, exception_id: int, decision: str, note: str = "") -> Optional[ExceptionModel]:
        exc = self.get_exception_by_id(exception_id)
        if exc:
            exc.status = "APPROVED" if decision.upper() == "APPROVE" else ("REJECTED" if decision.upper() == "REJECT" else "RESOLVED")
            exc.human_decision = decision
            exc.human_note = note
            exc.resolved_at = datetime.datetime.utcnow()
            self.db.commit()
            self.db.refresh(exc)
        return exc

    # ── Rule Registry ──────────────────────────────────────────────
    def get_all_rules(self, active_only: bool = True) -> List[RuleRegistryModel]:
        query = self.db.query(RuleRegistryModel)
        if active_only:
            query = query.filter(RuleRegistryModel.active == True)
        return query.all()

    def create_rule(self, pattern: str, category: str, effect: str, behavior: str = "DEDUCTION", created_by: str = "human") -> RuleRegistryModel:
        pattern_clean = pattern.lower().strip()
        existing = self.db.query(RuleRegistryModel).filter(RuleRegistryModel.pattern == pattern_clean).first()
        if existing:
            existing.normalized_category = category
            existing.financial_effect = effect
            existing.amount_behavior = behavior
            existing.created_by = created_by
            existing.active = True
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            rule = RuleRegistryModel(
                pattern=pattern_clean,
                normalized_category=category,
                financial_effect=effect,
                amount_behavior=behavior,
                created_by=created_by,
                active=True
            )
            self.db.add(rule)
            self.db.commit()
            self.db.refresh(rule)
            return rule

    # ── Agent Decisions Audit ─────────────────────────────────────
    def log_agent_decision(self, batch_id: str, exception_id: str, decision_type: str, decision: str, confidence: float, reasoning: str, context: Dict[str, Any] = None) -> AgentDecisionModel:
        ad = AgentDecisionModel(
            batch_id=batch_id,
            exception_id=exception_id,
            decision_type=decision_type,
            decision=decision,
            confidence=confidence,
            reasoning_summary=reasoning,
            input_context=context or {}
        )
        self.db.add(ad)
        self.db.commit()
        self.db.refresh(ad)
        return ad

    # ── Report Persistence ─────────────────────────────────────────
    def save_report(self, batch_id: str, report_type: str, metrics: Dict[str, Any], summary_json: Dict[str, Any], sku_breakdown_json: Dict[str, Any]) -> ReportModel:
        report = ReportModel(
            batch_id=batch_id,
            report_type=report_type,
            match_rate=float(metrics.get("match_rate", 0.0)),
            resolved_count=int(metrics.get("resolved_exceptions", 0)),
            unresolved_count=int(metrics.get("unresolved_exceptions", 0)),
            total_profit=float(metrics.get("total_profit", 0.0)),
            total_revenue=float(metrics.get("total_revenue", 0.0)),
            total_deductions=float(metrics.get("total_deductions", 0.0)),
            summary_json=summary_json,
            sku_breakdown_json=sku_breakdown_json
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_latest_report(self, batch_id: str) -> Optional[ReportModel]:
        return self.db.query(ReportModel).filter(ReportModel.batch_id == batch_id).order_by(ReportModel.created_at.desc()).first()
