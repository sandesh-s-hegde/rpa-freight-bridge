import uuid
from contextvars import ContextVar

correlation_id_ctx: ContextVar[str] = ContextVar(
    "correlation_id", default=str(uuid.uuid4())
)
