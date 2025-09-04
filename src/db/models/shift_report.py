from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Date, ForeignKey

from .base import Base


class ShiftReport(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date = mapped_column(Date, nullable=False)
    start_hour: Mapped[int] = mapped_column(nullable=True)
    start_minutes: Mapped[int] = mapped_column(nullable=True)
    end_hour: Mapped[int] = mapped_column(nullable=True)
    end_minutes: Mapped[int] = mapped_column(nullable=True)
    pause_hour: Mapped[int] = mapped_column(nullable=True)
    pause_minutes: Mapped[int] = mapped_column(nullable=True)
    count_dough: Mapped[int] = mapped_column(nullable=True)
    shift_type: Mapped[str] = mapped_column(nullable=False, comment="Day/Night")

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
