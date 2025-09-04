from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Date, Enum

from core.enums import Roles

from .base import Base


class ShiftReport(Base):
    date = mapped_column(Date, nullable=False)
    start_hour: Mapped[int] = mapped_column(nullable=False)
    start_minutes: Mapped[int] = mapped_column(nullable=False)
    end_hour: Mapped[int] = mapped_column(nullable=False)
    end_minutes: Mapped[int] = mapped_column(nullable=False)
    pause_hour: Mapped[int] = mapped_column(nullable=False)
    pause_minutes: Mapped[int] = mapped_column(nullable=False)
    role: Mapped[Roles] = mapped_column(Enum(Roles), nullable=False)

    @property
    def work_duration_minutes(self) -> int:
        start = self.start_hour * 60 + self.start_minutes
        end = self.end_hour * 60 + self.end_minutes
        pause = self.pause_hour * 60 + self.pause_minutes
        if end < start:
            end += 24 * 60
        return end - start - pause

    @property
    def work_duration_hours(self) -> int:
        return self.work_duration_minutes // 60
