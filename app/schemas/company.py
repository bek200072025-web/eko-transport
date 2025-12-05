from pydantic import BaseModel
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    phone: str
    region: str
    address: str | None = None
    description: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    region: str | None = None
    description: str | None = None
    is_verified: bool | None = None


class CompanyResponse(CompanyBase):
    id: int
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True
