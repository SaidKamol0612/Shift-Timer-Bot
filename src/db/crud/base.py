import logging

from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from core.config import settings

from db import db_helper
from ..models.user import User

# Generic type variables
M = TypeVar("M")  # SQLAlchemy model type (must have 'id' attribute)
S = TypeVar("S", bound=BaseModel)  # Pydantic schema for CRUD operations

log = logging.getLogger(__name__)


class BaseCRUD(Generic[M, S]):
    """
    Generic CRUD operations for SQLAlchemy models using separate Pydantic schemas
    for creation and update operations.
    """

    def __init__(self, model_type: Type[M]):
        self.MODEL_TYPE = model_type

    async def create(self, session: AsyncSession, schema: S) -> M:
        """Create a new record."""
        new_model = self.MODEL_TYPE(**schema.model_dump())
        session.add(new_model)
        try:
            await session.commit()
            await session.refresh(new_model)
        except IntegrityError as e:
            await session.rollback()
            log.warning("Catched exception: %s", e)
            raise e
        return new_model

    async def read(
        self, session: AsyncSession, filters: Optional[Dict[str, Any]] = None
    ) -> Optional[M]:
        """Retrieve a single record matching filters."""
        stmt = select(self.MODEL_TYPE)
        if filters:
            for field, value in filters.items():
                if hasattr(self.MODEL_TYPE, field):
                    stmt = stmt.where(getattr(self.MODEL_TYPE, field) == value)
                else:
                    raise ValueError(
                        f"Field '{field}' does not exist on {self.MODEL_TYPE.__name__}"
                    )
        return await session.scalar(stmt)

    async def read_all(
        self, session: AsyncSession, filters: Optional[Dict[str, Any]] = None
    ) -> List[M]:
        """Retrieve all records matching optional filters."""
        stmt = select(self.MODEL_TYPE)
        if filters:
            for field, value in filters.items():
                if hasattr(self.MODEL_TYPE, field):
                    stmt = stmt.where(getattr(self.MODEL_TYPE, field) == value)
                else:
                    raise ValueError(
                        f"Field '{field}' does not exist on {self.MODEL_TYPE.__name__}"
                    )
        result = await session.scalars(stmt)
        return result.all()

    async def update(
        self, session: AsyncSession, model_id: int, schema: S
    ) -> Optional[M]:
        """Update an existing record by ID."""
        model = await self.read(session, {"id": model_id})
        if not model:
            return None

        for field, value in schema.model_dump(exclude_unset=True).items():
            setattr(model, field, value)
        try:
            await session.commit()
            await session.refresh(model)
        except IntegrityError as e:
            await session.rollback()
            log.warning("Catched exception: %s", e)
            raise e

        return model

    async def delete(self, session: AsyncSession, model_id: int) -> bool:
        """Delete a record by ID."""
        model = await self.read(session, {"id": model_id})
        if model:
            await session.delete(model)
            await session.commit()
            return True
        return False
