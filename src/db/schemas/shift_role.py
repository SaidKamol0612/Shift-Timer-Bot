from pydantic import BaseModel

from datetime import date


class ShiftRoleSchema(BaseModel):
    date: date
    role_id: int
    shift_id: int
