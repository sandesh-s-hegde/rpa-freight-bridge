import logging
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.payloads import CapacityRequest
from services.uipath_client import UiPathService
from repositories.audit_repository import AuditRepository

logger = logging.getLogger("rpa-bridge")

class OrchestrationService:
    def __init__(self, db: AsyncSession, uipath_client: UiPathService):
        self.repository = AuditRepository(db)
        self.uipath = uipath_client

    async def process_booking_request(self, request: CapacityRequest) -> None:
        existing = await self.repository.get_by_transaction_id(request.transaction_id)
        if existing:
            logger.warning(f"Idempotency block: Transaction {request.transaction_id} already processed.")
            return

        success = await self.uipath.push_to_queue(request.model_dump(mode="json"))
        await self.repository.create_audit_record(request, success)