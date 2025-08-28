from .base import BaseCRUD
from ..models import User
from ..schemas import UserSchema


# -------------------------------
# CRUD class for User
# -------------------------------
class UserCRUD(BaseCRUD[User, UserSchema]):
    """
    Concrete CRUD class for User model.
    Inherits all methods from BaseCRUD:
      - create: insert new user
      - read: get user by id
      - read_all: get all users
      - update: update user by id
      - delete: delete user by id
    """

    def __init__(self):
        """
        Initialize UserCRUD with the User SQLAlchemy model.
        """
        super().__init__(User)


# Singleton instance for convenient usage throughout the project
user_crud = UserCRUD()
