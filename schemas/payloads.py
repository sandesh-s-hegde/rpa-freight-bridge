from datetime import date
from pydantic import BaseModel, Field


class CapacityRequest(BaseModel):
    transaction_id: str = Field(..., min_length=5)
    carrier_name: str = Field(..., min_length=2)
    vehicle_type: str = Field(..., min_length=3)
    pickup_date: date
    max_budget_eur: float = Field(..., gt=0)
