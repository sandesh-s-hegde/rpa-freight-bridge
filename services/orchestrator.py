import logging
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.payloads import CapacityRequest
from schemas.callbacks import RpaCallbackPayload
from services.uipath_client import UiPathService
from repositories.audit_repository import AuditRepository
from core.routing import CarrierRouter
from core.metrics import RPA_TASKS_DISPATCHED, RPA_TASKS_COMPLETED

logger = logging.getLogger("rpa-bridge")


class OrchestrationService:
    def __init__(self, db: AsyncSession, uipath_client: UiPathService):
        self.repository = AuditRepository(db)
        self.uipath = uipath_client

    async def process_booking_request(self, request: CapacityRequest) -> None:
        existing = await self.repository.get_by_transaction_id(request.transaction_id)
        if existing:
            logger.warning(
                f"Idempotency block: Transaction {request.transaction_id} already processed."
            )
            return

        target_queue = CarrierRouter.resolve_queue(request.carrier_name)
        logger.info(
            f"Routing transaction {request.transaction_id} to designated queue: {target_queue}"
        )

        success = await self.uipath.push_to_queue(
            payload=request.model_dump(mode="json"), target_queue=target_queue
        )
        await self.repository.create_audit_record(request, success)

        # Increment custom Prometheus metric
        if success:
            RPA_TASKS_DISPATCHED.labels(carrier_name=request.carrier_name).inc()

    async def process_rpa_callback(self, payload: RpaCallbackPayload) -> bool:
        existing = await self.repository.get_by_transaction_id(payload.transaction_id)
        if not existing:
            logger.error(
                f"Callback received for unknown transaction: {payload.transaction_id}"
            )
            return False

        await self.repository.update_transaction_state(
            transaction_id=payload.transaction_id,
            status=payload.status,
            confirmation_id=payload.confirmation_id,
            error_message=payload.error_message,
        )
        logger.info(f"Transaction {payload.transaction_id} updated to {payload.status}")

        RPA_TASKS_COMPLETED.labels(status=payload.status).inc()
        return True
