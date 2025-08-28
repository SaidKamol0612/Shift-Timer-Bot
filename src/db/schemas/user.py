from typing import Optional
from pydantic import BaseModel


# Pydantic schema for User model
class UserSchema(BaseModel):
    """
    Schema representing a User.

    Used for CRUD operations in UserCRUD.
    All fields are optional to allow partial updates.
    """

    id: Optional[int] = None
    tg_id: Optional[int]
    name: Optional[str]

    # User status flags
    is_superuser: Optional[bool] = False
