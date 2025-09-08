from pydantic import BaseModel

from datetime import date


class ShiftRoleSchema(BaseModel):
    date: date
    role_code: str
    shift_id: int
