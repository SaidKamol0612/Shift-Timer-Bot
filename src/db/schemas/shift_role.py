from pydantic import BaseModel

from datetime import date


class ShiftRole(BaseModel):
    date: date
    role_id: int
    shift_id: int
    is_approved: bool
