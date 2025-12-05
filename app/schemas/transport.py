from pydantic import BaseModel
from datetime import datetime


class TransportBase(BaseModel):
    category: str
    brand: str
    model: str
    year: int
    price_per_day: float
    transmission: str | None = None
    fuel_type: str | None = None
    seats: int | None = None


class TransportCreate(TransportBase):
    company_id: int


class TransportUpdate(BaseModel):
    category: str | None = None
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    price_per_day: float | None = None
    transmission: str | None = None
    fuel_type: str | None = None
    seats: int | None = None
