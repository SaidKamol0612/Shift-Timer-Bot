from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Date, ForeignKey, Enum

from core.enums import ShiftTypeENUM

from .base import Base


class Shift(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date = mapped_column(Date, nullable=False)
    start_hour: Mapped[int] = mapped_column(nullable=True)
    start_minute: Mapped[int] = mapped_column(nullable=True)
    end_hour: Mapped[int] = mapped_column(nullable=True)
    end_minute: Mapped[int] = mapped_column(nullable=True)
    pause_hours: Mapped[int] = mapped_column(nullable=True)
    pause_minutes: Mapped[int] = mapped_column(nullable=True)
    count_dough: Mapped[int] = mapped_column(nullable=True)
    shift_type: Mapped[ShiftTypeENUM] = mapped_column(
        Enum(ShiftTypeENUM, native_enum=False), nullable=False
    )
    is_approved: Mapped[bool] = mapped_column(nullable=False, default=False)

    @property
    def work_duration_minutes(self) -> int:
        start = self.start_hour * 60 + self.start_minute
        end = self.end_hour * 60 + self.end_minute
        pause = self.pause_hours * 60 + self.pause_minutes
        if end < start:
            end += 24 * 60

        duration = end - start - pause
        return max(duration, 0)

    @property
    def work_duration_hours(self) -> int:
        return self.work_duration_minutes // 60
