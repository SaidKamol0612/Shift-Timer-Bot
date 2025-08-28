from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseCRUD
from ..models import Subscription
from ..schemas import SubscriptionSchema


# -------------------------------
# CRUD class for User
# -------------------------------
class SubscriptionCRUD(BaseCRUD[Subscription, SubscriptionSchema]):
    """
    Concrete CRUD class for Subscription model.
    Inherits all methods from BaseCRUD:
      - create: insert new subscription
      - read: get subscription by id
      - read_all: get all subscription
      - update: update subscription by id
      - delete: delete subscription by id
    """

    def __init__(self):
        """
        Initialize SubscriptionCRUD with the Subscription SQLAlchemy model.
        """
        super().__init__(Subscription)

    async def read_all_by_status(self, session: AsyncSession, status: bool):
        """
        Retrieve all subscriptions filtered by their 'is_open' status.

        Args:
            session (AsyncSession): Async SQLAlchemy session.
            status (bool): Desired status (True for open, False for closed).

        Returns:
            List[Subscription]: List of subscription records matching the status.
        """
        stmt = select(self.MODEL_TYPE).where(self.MODEL_TYPE.is_open.is_(status))
        res = await session.scalars(stmt)
        return res.all()


# Singleton instance for convenient usage throughout the project
subscription_crud = SubscriptionCRUD()
