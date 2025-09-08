from pydantic import BaseModel
from datetime import date as PyDate
from typing import Optional


class ShiftSchema(BaseModel):
    user_id: int
    date: PyDate
    start_hour: Optional[int] = None
    start_minute: Optional[int] = None
    end_hour: Optional[int] = None
    end_minute: Optional[int] = None
    pause_hours: Optional[int] = None
    pause_minutes: Optional[int] = None
    count_dough: Optional[int] = None
    shift_type: str
    is_approved: Optional[bool] = False


class ShiftUpdateSchema(BaseModel):
    date: Optional[PyDate] = None
    start_hour: Optional[int] = None
    start_minutes: Optional[int] = None
    end_hour: Optional[int] = None
    end_minutes: Optional[int] = None
    pause_hour: Optional[int] = None
    pause_minutes: Optional[int] = None
    count_dough: Optional[int] = None
    shift_type: Optional[str] = None
    is_approved: Optional[bool] = None
