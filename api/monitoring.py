from datetime import datetime, timezone
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/v1/system", tags=["System"])

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "rpa-freight-bridge"
    }