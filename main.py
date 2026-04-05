from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.monitoring import router as monitoring_router
from api.audit import router as audit_router
from core.constants import ApiVersion
from core.database import engine, Base, AsyncSessionLocal
from core.exceptions import setup_exception_handlers
from core.http_client import HttpClient
from core.middleware import ProcessTimeMiddleware
from core.rate_limit import limiter, setup_rate_limiting
from core.security import verify_api_key
from schemas.payloads import CapacityRequest
from services.orchestrator import OrchestrationService
from services.uipath_client import UiPathService

tags_metadata = [
    {"name": "Orchestration", "description": "Core logic for bridging AI analytics with legacy RPA workers."},
    {"name": "Audit", "description": "Transaction history and paginated idempotency logs."},
    {"name": "System", "description": "Operational telemetry and health monitoring."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    HttpClient.get_client()
    yield
    await HttpClient.close_client()

app = FastAPI(
    title="RPA Legacy Freight Bridge API",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=f"{ApiVersion.V1.value}/docs",
    redoc_url=None,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ProcessTimeMiddleware)

setup_exception_handlers(app)
setup_rate_limiting(app)

app.include_router(monitoring_router)
app.include_router(audit_router)

Instrumentator().instrument(app).expose(app)

def get_uipath_service() -> UiPathService:
    return UiPathService()

async def execute_background_orchestration(payload: CapacityRequest, uipath_client: UiPathService):
    async with AsyncSessionLocal() as db:
        orchestrator = OrchestrationService(db, uipath_client)
        await orchestrator.process_booking_request(payload)

@app.post(
    f"{ApiVersion.V1.value}/orchestrate",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Orchestration"],
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit("10/minute")
async def trigger_legacy_booking(
    request: Request,
    payload: CapacityRequest,
    background_tasks: BackgroundTasks,
    uipath_client: UiPathService = Depends(get_uipath_service)
):
    background_tasks.add_task(execute_background_orchestration, payload, uipath_client)

    return {
        "status": "processing",
        "transaction_id": payload.transaction_id,
        "message": "Webhook accepted. RPA execution dispatched to background worker."
    }