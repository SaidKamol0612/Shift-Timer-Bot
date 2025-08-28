from typing import Optional
from pydantic import BaseModel


# -------------------------------
# Pydantic schema for Subscription model
# -------------------------------
class SubscriptionSchema(BaseModel):
    """
    Pydantic schema representing a Subscription.

    Used for CRUD operations in SubscriptionCRUD.
    All fields are optional to allow partial updates.
    """

    id: Optional[int]  # Primary key from database
    chat_id: Optional[str]  # Telegram chat ID (group, supergroup, or channel)
    link: Optional[str]  # Invite link or username of the chat
    is_open: Optional[bool]  # Indicates if the subscription is currently active
