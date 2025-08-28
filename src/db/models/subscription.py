from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Subscription(Base):
    """
    SQLAlchemy model representing a subscription requirement for a Telegram chat.

    Attributes:
        chat_id (str): Unique identifier of the chat (group/channel) the user should subscribe to.
        link (str): Invite link or username of the chat.
        is_open (bool): Flag indicating whether the subscription requirement is currently active.
    """

    # Telegram chat ID (group, supergroup, or channel)
    chat_id: Mapped[str] = mapped_column(String, nullable=False)

    # Link or username of the chat
    link: Mapped[str] = mapped_column(String, nullable=False)

    # Status indicating if the subscription is open/active
    is_open: Mapped[bool] = mapped_column(nullable=False)
