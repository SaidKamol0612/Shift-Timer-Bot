from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum

from .base import Base
from core.enums import RoleENUM


class Role(Base):
    code: Mapped[str] = mapped_column(String(1), nullable=False)
    role: Mapped[RoleENUM] = mapped_column(
        Enum(RoleENUM, native_enum=False), nullable=False, unique=True
    )
    day_rate: Mapped[int] = mapped_column(default=0, server_default="0")
    night_rate: Mapped[int] = mapped_column(default=0, server_default="0")
