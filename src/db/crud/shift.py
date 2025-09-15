from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date as PyDate

from .base import BaseCRUD
from ..models import Shift, User, ShiftRole
from ..schemas import ShiftSchema


class ShiftCRUD(BaseCRUD[Shift, ShiftSchema]):

    def __init__(self):
        self.model = Shift
        super().__init__(Shift)

    async def get_workers_by_date_role(
        self,
        session: AsyncSession,
        date: PyDate,
    ):
        stmt = (
            select(Shift)
            .join(ShiftRole, ShiftRole.shift_id == Shift.id)
            .where(ShiftRole.role_code == "T")
            .where(Shift.date == date)
            .where(Shift.shift_type == "DAY")
            .where(Shift.is_approved.is_(True))
        )

        res = await session.execute(stmt)
        return res.scalars().all()


shift_crud = ShiftCRUD()
