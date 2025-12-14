from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CustomerBase(BaseModel):
    name: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = None


class Customer(CustomerBase):
    id: int
    created_on: datetime
    updated_on: datetime

    class Config:
        from_attributes = True