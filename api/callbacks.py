from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from core.hmac_validator import verify_webhook_signature
from core.constants import ApiVersion
from schemas.callbacks import RpaCallbackPayload
from services.orchestrator import OrchestrationService
from services.uipath_client import UiPathService

# Note: We replaced standard API key validation with strict HMAC signature verification
router = APIRouter(
    prefix=f"{ApiVersion.V1.value}/callback",
    tags=["Callbacks"],
    dependencies=[Depends(verify_webhook_signature)]
)


def get_uipath_service() -> UiPathService:
    return UiPathService()


@router.patch("/rpa", status_code=status.HTTP_200_OK)
async def handle_rpa_completion(
        request: Request,
        payload: RpaCallbackPayload,
        db: AsyncSession = Depends(get_db_session),
        uipath_client: UiPathService = Depends(get_uipath_service)
):
    orchestrator = OrchestrationService(db, uipath_client)
    success = await orchestrator.process_rpa_callback(payload)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction ID not found."
        )

    return {
        "status": "acknowledged",
        "transaction_id": payload.transaction_id,
        "final_state": payload.status
    }