from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, ForeignKey

from .base import Base


class ShiftRole(Base):
    date = mapped_column(Date, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    shift_id: Mapped[int] = mapped_column(
        ForeignKey("shift_reports.id"), nullable=False
    )
