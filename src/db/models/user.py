from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """
    SQLAlchemy model representing a Telegram user.
    """

    # Telegram user ID, must be unique per user
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Username of the Telegram user
    username: Mapped[str] = mapped_column(String, nullable=False)

    # Flag indicating if the user has superuser/admin privileges
    is_superuser: Mapped[bool] = mapped_column(default=False)

    # Flag indicating if the user is blocked from chat
    is_chat_blocked: Mapped[bool] = mapped_column(default=False)
