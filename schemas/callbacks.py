from pydantic import BaseModel, Field

class RpaCallbackPayload(BaseModel):
    transaction_id: str = Field(..., min_length=5)
    status: str = Field(..., pattern="^(completed|failed)$")
    confirmation_id: str | None = None
    error_message: str | None = None