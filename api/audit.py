from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from core.security import verify_api_key
from core.constants import ApiVersion
from repositories.audit_repository import AuditRepository

router = APIRouter(prefix=f"{ApiVersion.V1.value}/audit", tags=["Audit"], dependencies=[Depends(verify_api_key)])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_transaction_history(
        limit: int = Query(50, ge=1, le=100),
        cursor: str | None = Query(None, description="Provide the last transaction_id from the previous page"),
        db: AsyncSession = Depends(get_db_session)
):
    repository = AuditRepository(db)
    records = await repository.get_recent_audits(limit=limit, cursor=cursor)

    next_cursor = records[-1].transaction_id if len(records) == limit else None

    return {
        "data": records,
        "meta": {
            "limit": limit,
            "next_cursor": next_cursor,
            "count": len(records)
        }
    }