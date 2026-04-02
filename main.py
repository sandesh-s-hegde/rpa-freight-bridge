from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from api.monitoring import router as monitoring_router
from core.database import engine, Base, get_db_session
from core.exceptions import setup_exception_handlers
from core.middleware import ProcessTimeMiddleware
from core.rate_limit import limiter, setup_rate_limiting
from core.security import verify_api_key
from core.constants import ApiVersion
from schemas.payloads import CapacityRequest
from services.uipath_client import UiPathService
from services.orchestrator import OrchestrationService

tags_metadata = [
    {"name": "Orchestration", "description": "Core logic for bridging AI analytics with legacy RPA workers."},
    {"name": "System", "description": "Operational telemetry and health monitoring."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="RPA Legacy Freight Bridge API",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=f"{ApiVersion.V1}/docs",
    redoc_url=None,
    lifespan=lifespan
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
setup_rate_limiting(app)
app.include_router(monitoring_router)

def get_uipath_service() -> UiPathService:
    return UiPathService()

def get_orchestrator(
    db: AsyncSession = Depends(get_db_session),
    uipath_client: UiPathService = Depends(get_uipath_service)
) -> OrchestrationService:
    return OrchestrationService(db, uipath_client)

@app.post(
    f"{ApiVersion.V1}/orchestrate",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Orchestration"],
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit("10/minute")
async def trigger_legacy_booking(
    request: Request,
    payload: CapacityRequest,
    background_tasks: BackgroundTasks,
    orchestrator: OrchestrationService = Depends(get_orchestrator)
):
    background_tasks.add_task(orchestrator.process_booking_request, payload)

    return {
        "status": "processing",
        "transaction_id": payload.transaction_id,
        "message": "Webhook accepted. RPA execution dispatched to background worker."
    }