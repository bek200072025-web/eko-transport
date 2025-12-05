from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum
from typing import Optional


class BookingStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    cancelled = "cancelled"
    completed = "completed"


class BookingCreate(BaseModel):
    company_id: int
    car_id: int
    start_date: date
    end_date: date


class BookingResponse(BaseModel):
    id: int
    company_id: int
    car_id: int
    user_id: int
    start_date: date
    end_date: date
    total_price: float
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True
