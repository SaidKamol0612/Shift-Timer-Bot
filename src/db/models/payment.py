from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Date

from .base import Base


class Payment(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date = mapped_column(Date, nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str]
