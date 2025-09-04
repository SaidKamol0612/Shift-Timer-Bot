from pydantic import BaseModel, Field

from core.enums import RoleENUM


class RoleSchema(BaseModel):
    code: str = Field(..., examples=["X", "P", "T", "O"])
    role: RoleENUM
    day_rate: int
    night_rate: int
