from pydantic import BaseModel
from datetime import datetime


class PaymentBase(BaseModel):
    booking_id: int
    amount: float
    method: str


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    status: str | None = None
    amount: float | None = None
    method: str | None = None


class PaymentResponse(PaymentBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
