from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    fullname: str
    email: str
    password: str
    phone: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass