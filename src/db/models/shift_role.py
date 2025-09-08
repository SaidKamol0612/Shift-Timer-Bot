from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, ForeignKey

from .base import Base


class ShiftRole(Base):
    date = mapped_column(Date, nullable=False)
    role_code: Mapped[str] = mapped_column(nullable=False)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"), nullable=False)
