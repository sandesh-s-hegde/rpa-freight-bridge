from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Boolean
from core.database import Base

class TransactionAudit(Base):
    __tablename__ = "transaction_audit"

    transaction_id = Column(String, primary_key=True, index=True)
    carrier_name = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    max_budget_eur = Column(Float, nullable=False)
    uipath_acknowledged = Column(Boolean, default=False)
    status = Column(String, default="queued", index=True)
    confirmation_id = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    is_dlq = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))