import logging
from schemas.payloads import CapacityRequest

logger = logging.getLogger("rpa-bridge")

class TransactionAuditService:
    @staticmethod
    async def log_request(request: CapacityRequest, status: str) -> None:
        logger.info(f"Auditing Transaction: {request.transaction_id} | Status: {status}")