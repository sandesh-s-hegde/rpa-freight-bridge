from fastapi import FastAPI, Depends, status
from schemas.payloads import CapacityRequest
from services.uipath_client import UiPathService
from core.exceptions import setup_exception_handlers
from api.monitoring import router as monitoring_router

app = FastAPI(title="RPA Legacy Freight Bridge API", version="1.0.0")

setup_exception_handlers(app)
app.include_router(monitoring_router)


def get_uipath_service() -> UiPathService:
    return UiPathService()


@app.post("/api/v1/orchestrate", status_code=status.HTTP_202_ACCEPTED, tags=["Orchestration"])
async def trigger_legacy_booking(
        request: CapacityRequest,
        uipath_service: UiPathService = Depends(get_uipath_service)
):
    success = await uipath_service.push_to_queue(request.model_dump(mode="json"))

    return {
        "status": "queued",
        "transaction_id": request.transaction_id,
        "uipath_acknowledged": success
    }