from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List, Optional

from db.models import Shift, Payment
from db.crud import shift_role_crud
from services.role_service import role_service
from core.enums import ShiftTypeENUM


class ReportService:
    """Service for generating and parsing reports"""

    async def _get_roles_and_daily_fee(
        self,
        session: AsyncSession,
        shift: Shift,
    ) -> Tuple[List[str], int]:
        roles = await shift_role_crud.read_all(
            session=session, filters={"shift_id": shift.id}
        )
        worked_roles = []
        shift_fee = 0
        for sh_r in roles:
            role = role_service.read_role(code=sh_r.role_code)
            worked_roles.append(role.title)
            if shift.shift_type == ShiftTypeENUM.DAY:
                if role.code == "O":
                    shift_fee += role.day_rate_for_hour
                else:
                    shift_fee += role.day_rate_for_hour * shift.work_duration_hours
            else:
                shift_fee += role.night_rate_for_dough * shift.count_dough
        return worked_roles, shift_fee

    async def _gen_report_by_day_shift(
        self, session: AsyncSession, shift: Shift, shorter: bool
    ) -> Tuple[str, int]:
        worked_roles, shift_fee = await self._get_roles_and_daily_fee(session, shift)

        if shorter:
            role_codes = "".join([r[0] for r in worked_roles])
            report = f"{shift.date} | {role_codes} | {shift_fee}"
        else:
            start = f"{shift.start_hour:02d}:{shift.start_minute:02d}"
            end = f"{shift.end_hour:02d}:{shift.end_minute:02d}"
            pause = f"{shift.pause_hours:02d}:{shift.pause_minutes:02d}"
            roles_str = " ".join(worked_roles)
            report = (
                f"<b>Sana:</b> {shift.date}\n"
                f"<b>Smena:</b> ☀️ Kunduzgi\n"
                f"<b>Ish vaqti:</b> {start} - {end}\n"
                f"<b>Tanafus:</b> {pause}\n"
                f"<b>Qilingan ishlar:</b> {roles_str}\n"
                f"<b>Kunlik to'lov:</b> {shift_fee}\n"
                f"=============================="
            )
        return report, shift_fee

    async def _gen_report_by_night_shift(
        self, session: AsyncSession, shift: Shift, shorter: bool
    ) -> Tuple[str, int]:
        roles, daily = await self._get_roles_and_daily_fee(session, shift)

        if shorter:
            report = f"{shift.date} | {daily}"
        else:
            roles_str = " ".join(roles)
            report = (
                f"<b>Sana:</b> {shift.date}\n"
                f"<b>Smena:</b> 🌙 Tungi\n"
                f"<b>Xamir soni:</b> {shift.count_dough}\n"
                f"<b>Qilingan ishlar:</b> {roles_str}\n"
                f"<b>Kunlik to'lov:</b> {daily}\n"
                f"=============================="
            )

        return report, daily

    async def generate_report_by_shift(
        self, session: AsyncSession, shift: Shift, shorter: Optional[bool] = True
    ) -> Tuple[str, int]:
        match shift.shift_type:
            case ShiftTypeENUM.DAY:
                return await self._gen_report_by_day_shift(session, shift, shorter)
            case ShiftTypeENUM.NIGHT:
                return await self._gen_report_by_night_shift(session, shift, shorter)

    def generate_report_by_payment(
        self, payment: Payment, shorter: Optional[bool] = True
    ) -> Tuple[str, int]:
        if shorter:
            return f"{payment.date} | {payment.amount}", payment.amount
        else:
            return (
                f"<b>Sana:</b> {payment.date}\n"
                f"<b>Miqdor:</b> {payment.amount}\n"
                f"<b>Izoh:</b> {payment.comment}\n"
                "==============================",
                payment.amount,
            )


report_service = ReportService()
