from typing import Optional
from pydantic import BaseModel


# -------------------------------
# Pydantic schema for User model
# -------------------------------
class UserSchema(BaseModel):
    """
    Schema representing a User.
    
    Used for CRUD operations in UserCRUD.
    All fields are optional to allow partial updates.
    """

    id: Optional[int]  # Database primary key
    tg_id: Optional[int]  # Telegram user ID
    username: Optional[str]  # Telegram username

    # User status flags
    is_admin: Optional[bool] = False  # Admin privileges
    is_chat_blocked: Optional[bool] = False  # Chat blocked flag
