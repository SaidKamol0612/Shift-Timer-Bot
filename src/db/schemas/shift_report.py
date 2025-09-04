from pydantic import BaseModel, Field

from core.enums import Roles


class ShiftReportSchema(BaseModel):
    date = Field
    start_hour: int
    start_minutes: int
    end_hour: int
    end_minutes: int
    pause_hour: int
    pause_minutes: int
    role: Roles
