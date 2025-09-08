from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from states import BotState
from db import db_helper
from db.crud import shift_crud, user_crud, payment_crud
from services import report_service

router = Router()


@router.callback_query(F.data == "report", BotState.WORKER_MENU)
async def handle_report(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    user = call_back.from_user

    async with db_helper.session_factory() as session:
        curr = await user_crud.read(session=session, filters={"tg_id": user.id})
        shifts = await shift_crud.read_all(
            session=session, filters={"user_id": curr.id, "is_approved": True}
        )
        payments = await payment_crud.read_all(
            session=session, filters={"user_id": curr.id}
        )

        # Total salary
        salary = 0
        # Shifts
        res = "<b>Ishlangan kunlar</b>"
        if not shifts:
            res += " <b>yo'q</b>\n"
        for sh in shifts:
            report, shift_fee = await report_service.generate_report_by_shift(
                session=session, shift=sh
            )
            res += "\n" + report
            salary += shift_fee

        # Payments
        res += "\n<b>To'lovlar</b>"
        if not payments:
            res += " <b>yo'q</b>\n"
        for p in payments:
            report, amount = report_service.generate_report_by_payment(payment=p)
            res += "\n" + report
            salary -= amount
        res += f"\n<b>Jami oylik:</b> {salary}"

    await call_back.message.answer(text=res)
