from sqlalchemy.ext.asyncio import AsyncSession
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
            uipath_acknowledged=acknowledged
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record