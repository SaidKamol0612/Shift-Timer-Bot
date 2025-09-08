from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from datetime import date

from states import BotState
from db import db_helper
from db.crud import user_crud, payment_crud
from db.schemas import PaymentSchema
from keyboards.reply import workers_kb
from keyboards.inline import InlineKeyboards
from utils import AdminUtil


router = Router()


@router.callback_query(F.data == "pay", BotState.ADMIN_MENU)
async def handle_pay(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    await state.update_data(date=date.today())
    text = "✅ To'lov jarayoni boshandi.\n" "👤 To'lamoqchi bo'lgan ishchini tanlang."
    async with db_helper.session_factory() as session:
        workers = await user_crud.read_all(
            session=session, filters={"is_superuser": False}
        )

    await state.set_state(BotState.SetPayment.CHOOSE_WORKER)
    await call_back.message.delete()
    await call_back.message.answer(text=text, reply_markup=workers_kb(models=workers))


@router.message(F.text, BotState.SetPayment.CHOOSE_WORKER)
async def choose_worker_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "❌ Bekor qilish":
        text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
        await state.set_state(BotState.ADMIN_MENU)
        kb = InlineKeyboards.admin_menu()
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

        await state.update_data(user_id=user.id)
        await state.set_state(BotState.SetPayment.SET_AMOUNT)

        await message.reply("✅ Qabul qilindi.", reply_markup=ReplyKeyboardRemove())
        text = (
            "💲 Endi to'lov <b>miqdorini</b> jo'nating.\n"
            "/cancel orqali jarayoni bekor qilishingiz mumkin."
        )
        await message.answer(text=text)


@router.message(F.text, BotState.SetPayment.SET_AMOUNT)
async def handle_amount(message: Message, state: FSMContext):
    amount = message.text
    if not amount.isdigit():
        await message.answer("⚠️ To'lov miqdori to'g'ri formatda bo'lishi kerak.")
        return
    else:
        await state.update_data(amount=int(amount))
        await state.set_state(BotState.SetPayment.SET_COMMENT)
        await message.reply("✅ Qabul qilindi.")
        text = (
            "ℹ️ Endi to'lov uchun <b>izoh</b> jo'nating. Masalan, avans, oylik yoki boshqa.\n"
            "/cancel orqali jarayoni bekor qilishingiz mumkin."
        )
        await message.answer(text=text)


@router.message(F.text, BotState.SetPayment.SET_COMMENT)
async def handle_comment(message: Message, state: FSMContext):
    comment = message.text
    data = await state.get_data()

    async with db_helper.session_factory() as session:
        user = await user_crud.read(
            session=session, filters={"id": data.get("user_id")}
        )
        await payment_crud.create(
            session=session,
            schema=PaymentSchema(
                user_id=data.get("user_id"),
                date=data.get("date"),
                amount=data.get("amount"),
                comment=comment,
            ),
        )

    await message.reply("✅ Qabul qilindi.")
    text = (
        f"<b>📅 Sana:</b> {data.get('date')}\n"
        f"WORKER_NAME <b>{data.get('amount')}</b> miqdorida to'lov amalga oshirildi.\n"
        f"<b>ℹ️ Izoh:</b> {comment}\n"
    )
    await AdminUtil.send_msg(
        chat_id=user.tg_id,
        msg=("Sizga admindan xabar:\n" + text.replace("WORKER_NAME", f"Sizga")),
    )

    await message.answer(text=text.replace("WORKER_NAME", f"<b>{user.name}</b>ga"))
    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    await state.set_state(BotState.ADMIN_MENU)
    kb = InlineKeyboards.Menus.admin_menu()
    await message.answer(text=text, reply_markup=kb)
