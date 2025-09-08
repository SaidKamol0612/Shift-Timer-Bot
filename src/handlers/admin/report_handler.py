from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states import BotState
from db import db_helper
from db.crud import shift_crud, user_crud, payment_crud
from services import report_service
from keyboards.inline import InlineKeyboards
from keyboards.reply import workers_kb

router = Router()


@router.callback_query(F.data == "report", BotState.ADMIN_MENU)
async def handle_report(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    text = "👤 Hisobotini ko'rmoqchi bo'lgan ishchini tanlang."
    async with db_helper.session_factory() as session:
        workers = await user_crud.read_all(
            session=session, filters={"is_superuser": False}
        )

    await state.set_state(BotState.GetReport.CHOOSE_WORKER)
    await call_back.message.delete()
    await call_back.message.answer(text=text, reply_markup=workers_kb(models=workers))


@router.message(F.text, BotState.GetReport.CHOOSE_WORKER)
async def choose_worker_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "❌ Bekor qilish":
        text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
        await state.set_state(BotState.ADMIN_MENU)
        kb = InlineKeyboards.Menus.admin_menu()
        await message.answer(
            text="❌ Bekor qilindi", reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(text=text, reply_markup=kb)
        return
    else:
        async with db_helper.session_factory() as session:
            user = await user_crud.read(session=session, filters={"name": text})
            if not user:
                await message.answer("⚠️ Bunday ishchi yo'q.")
            shifts = await shift_crud.read_all(
                session=session, filters={"user_id": user.id, "is_approved": True}
            )
            payments = await payment_crud.read_all(
                session=session, filters={"user_id": user.id}
            )

            # Total salary
            salary = 0
            # Shifts
            res = f"<b>{user.name}</b>ning oylik hisoboti.\n" "<b>Ishlangan kunlar</b>"
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
                report, amount = report_service.generate_report_by_payment(
                    payment=p
                )
                res += "\n" + report
                salary -= amount
            res += f"\n<b>Jami oylik:</b> {salary}"

        await message.answer(text=res)
