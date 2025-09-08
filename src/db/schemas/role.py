from pydantic import BaseModel
from typing import Literal

from core.enums import RoleENUM


class RoleSchema(BaseModel):
    code: Literal["X", "P", "T", "O"]
    title: str
    day_rate_for_hour: int
    night_rate_for_dough: int
