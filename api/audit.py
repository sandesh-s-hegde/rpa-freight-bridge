from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from core.security import verify_api_key
from repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"], dependencies=[Depends(verify_api_key)])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_transaction_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    repository = AuditRepository(db)
    records = await repository.get_recent_audits(limit=limit, offset=offset)
    return {
        "data": records,
        "meta": {"limit": limit, "offset": offset, "count": len(records)}
    }