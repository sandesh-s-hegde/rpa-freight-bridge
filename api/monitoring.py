from datetime import datetime, timezone
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db_session

router = APIRouter(prefix="/api/v1/system", tags=["System"])

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db_session)):
    db_status = "unhealthy"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "operational"
    except Exception:
        pass

    return {
        "status": "operational" if db_status == "operational" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": "rpa-freight-bridge",
        "dependencies": {
            "database": db_status
        }
    }