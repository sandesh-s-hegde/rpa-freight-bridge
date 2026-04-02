from sqlalchemy.ext.asyncio import AsyncSession
from schemas.payloads import CapacityRequest
from models.transaction import TransactionAudit
from services.uipath_client import UiPathService

class OrchestrationService:
    def __init__(self, db: AsyncSession, uipath_client: UiPathService):
        self.db = db
        self.uipath = uipath_client

    async def process_booking_request(self, request: CapacityRequest) -> None:
        success = await self.uipath.push_to_queue(request.model_dump(mode="json"))

        audit_record = TransactionAudit(
            transaction_id=request.transaction_id,
            carrier_name=request.carrier_name,
            vehicle_type=request.vehicle_type,
            max_budget_eur=request.max_budget_eur,
            uipath_acknowledged=success
        )

        self.db.add(audit_record)
        await self.db.commit()