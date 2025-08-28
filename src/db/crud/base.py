from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# M — type of SQLAlchemy model (must have 'id' attribute)
# S — type of Pydantic schema, must inherit from BaseModel
M = TypeVar("M")
S = TypeVar("S", bound=BaseModel)


class BaseCRUD(Generic[M, S]):
    MODEL_TYPE: Type[M]

    def __init__(self, model_type: Type[M]):
        self.MODEL_TYPE = model_type

    async def create(self, session: AsyncSession, schema: S) -> M:
        """
        Insert a new record using any Pydantic schema derived from BaseModel.
        """
        new_model = self.MODEL_TYPE(**schema.model_dump())
        session.add(new_model)
        await session.commit()
        await session.refresh(new_model)
        return new_model

    async def read(self, session: AsyncSession, model_id: int) -> Optional[M]:
        """
        Retrieve an existing record by its ID, or None if it does not exist.
        """
        stmt = select(self.MODEL_TYPE).where(self.MODEL_TYPE.id == model_id)
        result = await session.scalar(stmt)
        return result

    async def read_all(self, session: AsyncSession) -> List[M]:
        """
        Retrieve all existing records of the model.
        Returns a list of model instances.
        """
        stmt = select(self.MODEL_TYPE)
        result = await session.scalars(stmt)
        return result.all()

    async def update(
        self, session: AsyncSession, model_id: int, schema: S
    ) -> Optional[M]:
        """
        Update an existing record using data from a Pydantic schema.
        Returns the updated model, or None if not found.
        """
        model = await self.read(session=session, model_id=model_id)
        if not model:
            return None

        for field, value in schema.model_dump().items():
            setattr(model, field, value)

        await session.commit()
        await session.refresh(model)
        return model

    async def delete(self, session: AsyncSession, model_id: int) -> bool:
        """
        Delete an existing record by its ID.
        Returns True if deleted, False if not found.
        """
        model = await self.read(session=session, model_id=model_id)
        if model:
            await session.delete(model)
            await session.commit()
            return True
        return False
