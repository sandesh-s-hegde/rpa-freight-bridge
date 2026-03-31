from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from api.monitoring import router as monitoring_router
from core.exceptions import setup_exception_handlers
from core.middleware import ProcessTimeMiddleware
from core.security import verify_api_key
from core.constants import ApiVersion
from schemas.payloads import CapacityRequest
from services.uipath_client import UiPathService

tags_metadata = [
    {
        "name": "Orchestration",
        "description": "Core logic for bridging AI analytics with legacy RPA workers.",
    },
    {
        "name": "System",
        "description": "Operational telemetry and health monitoring.",
    },
]

app = FastAPI(
    title="RPA Legacy Freight Bridge API",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=f"{ApiVersion.V1}/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
app.add_middleware(ProcessTimeMiddleware)

setup_exception_handlers(app)
app.include_router(monitoring_router)

async def get_uipath_service() -> UiPathService:
    return UiPathService()

@app.post(
    f"{ApiVersion.V1}/orchestrate",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Orchestration"],
    dependencies=[Depends(verify_api_key)]
)
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