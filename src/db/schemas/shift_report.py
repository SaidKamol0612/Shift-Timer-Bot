from pydantic import BaseModel
from datetime import date
from typing import Optional


class ShiftReportSchema(BaseModel):
    user_id: int
    date: date
    start_hour: Optional[int]
    start_minutes: Optional[int]
    end_hour: Optional[int]
    end_minutes: Optional[int]
    pause_hour: Optional[int]
    pause_minutes: Optional[int]
    count_dough: Optional[int]
    shift_type: str
