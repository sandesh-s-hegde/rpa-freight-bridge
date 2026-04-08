from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.transaction import TransactionAudit
from schemas.payloads import CapacityRequest

class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_audit_record(self, request: CapacityRequest, acknowledged: bool) -> TransactionAudit:
        record = TransactionAudit(
            transaction_id=request.transaction_id,
            carrier_name=request.carrier_name,
            vehicle_type=request.vehicle_type,
            max_budget_eur=request.max_budget_eur,
            uipath_acknowledged=acknowledged,
            status="processing" if acknowledged else "failed"
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_by_transaction_id(self, transaction_id: str) -> TransactionAudit | None:
        stmt = select(TransactionAudit).where(TransactionAudit.transaction_id == transaction_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_recent_audits(self, limit: int = 50, offset: int = 0):
        stmt = select(TransactionAudit).order_by(TransactionAudit.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_transaction_state(self, transaction_id: str, status: str, confirmation_id: str | None = None, error_message: str | None = None) -> None:
        stmt = (
            update(TransactionAudit)
            .where(TransactionAudit.transaction_id == transaction_id)
            .values(status=status, confirmation_id=confirmation_id, error_message=error_message)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def update_transaction_state(self, transaction_id: str, status: str, confirmation_id: str | None = None,
                                       error_message: str | None = None) -> None:
        is_dlq = True if status == "failed" else False

        stmt = (
            update(TransactionAudit)
            .where(TransactionAudit.transaction_id == transaction_id)
            .values(
                status=status,
                confirmation_id=confirmation_id,
                error_message=error_message,
                is_dlq=is_dlq
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()