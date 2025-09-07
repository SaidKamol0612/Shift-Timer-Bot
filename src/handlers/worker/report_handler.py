from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states import BotState
from db.models import ShiftReport
from db import db_helper
from db.crud import shift_role_crud, role_crud, shift_report_crud, user_crud

router = Router()


class ReportService:
    """Service for generating and parsing reports"""

    async def get_roles(
        self,
        session: AsyncSession,
        shift_id: int,
        worked_hours: int | None = None,
        type: str = "day",
        count_dough: int | None = None,
    ):
        roles = await shift_role_crud.read_all(
            session=session, filters={"shift_id": shift_id}
        )
        names = []
        daily = 0
        for sh in roles:
            role = await role_crud.read(session=session, filters={"id": sh.role_id})
            names.append(role.role.title())
            if type == "day":
                daily += role.day_rate * worked_hours
            else:
                daily += role.day_rate * count_dough
        return (" ".join(names), daily)

    async def parse_report(self, session: AsyncSession, shift_report: ShiftReport):
        if shift_report.shift_type == "day":
            count_dough = (
                f"{shift_report.start_hour:02d}:{shift_report.start_minutes:02d}"
            )
            end = f"{shift_report.end_hour:02d}:{shift_report.end_minutes:02d}"
            roles, daily = await self.get_roles(
                session=session,
                shift_id=shift_report.id,
                worked_hours=shift_report.work_duration_hours,
                type="day",
            )
            report = (
                f"<b>Sana:</b> {shift_report.date}\n"
                f"<b>Smena:</b> ☀️ Kunduzgi\n"
                f"<b>Ish vaqti:</b> {count_dough} - {end}\n"
                f"<b>Tanafus:</b> {shift_report.pause_hour} soat\n"
                f"<b>Qilingan ishlar:</b> {roles}\n"
                f"<b>Kunlik to'lov:</b> {daily}\n"
                f"=============================="
            )
        else:
            count_dough = shift_report.count_dough
            roles, daily = await self.get_roles(
                session=session,
                shift_id=shift_report.id,
                type="night",
                count_dough=shift_report.count_dough,
            )
            report = (
                f"<b>Sana:</b> {shift_report.date}\n"
                f"<b>Smena:</b> 🌙 Tungi\n"
                f"<b>Xamir soni:</b> {count_dough}\n"
                f"<b>Qilingan ishlar:</b> {roles}\n"
                f"<b>Kunlik to'lov:</b> {daily}\n"
                f"=============================="
            )
        return (report, daily)


report_service = ReportService()


@router.callback_query(F.data == "report", BotState.WORKER_MENU)
async def handle_report(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    user = call_back.from_user

    async with db_helper.session_factory() as session:
        curr = await user_crud.read(session=session, filters={"tg_id": user.id})
        shifts = await shift_report_crud.read_all(
            session=session, filters={"user_id": curr.id, "is_approved": True}
        )
        salary = 0
        res = "<b>Ishlangan kunlar</b>"
        if not shifts:
            res += " <b>yo'q</b>"
        for sh in shifts:
            report, daily = await report_service.parse_report(
                session=session, shift_report=sh
            )
            res += "\n" + report
            salary += daily
        res += f"\n<b>Jami oylik:</b> {salary}"

    await call_back.message.answer(text=res)
