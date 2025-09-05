from pydantic import BaseModel
from datetime import date
from typing import Optional


class ShiftReportSchema(BaseModel):
    user_id: int
    date: date
    start_hour: Optional[int] = None
    start_minutes: Optional[int] = None
    end_hour: Optional[int] = None
    end_minutes: Optional[int] = None
    pause_hour: Optional[int] = None
    pause_minutes: Optional[int] = None
    count_dough: Optional[int] = None
    shift_type: str
