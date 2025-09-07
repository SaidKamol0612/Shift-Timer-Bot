from pydantic import BaseModel
from datetime import date as PyDate
from typing import Optional


class PaymentSchema(BaseModel):
    user_id: int
    date: PyDate
    amount: int
    comment: str


class PaymentUpdateSchema(BaseModel):
    user_id: Optional[int]
    date: Optional[PyDate]
    amount: Optional[int]
    comment: Optional[str]
