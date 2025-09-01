from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date

from states.bot_state import BotState
from keyboards.inline import time_keyboard, WORKER_MENU

# Initialize router
router = Router()


@router.callback_query(F.data == "day_shift", BotState.WORKER_MENU)
async def call_day_shift_handle(call_back: CallbackQuery, state: FSMContext):
    today = date.today()
    text = (
        f"<b>📅 Bugungi sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        "\nIltimos, endi pastdagi tugmalar yordamida ish boshlagan vaqtingizni tanlang."
    )
    await state.update_data(date=today)
    await state.set_state(BotState.SET_START)
    await call_back.message.edit_text(text=text, reply_markup=time_keyboard())


async def handle_current(call_back: CallbackQuery, state: FSMContext):
    parts = call_back.data.split("_")[1].split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])
    text = f"🕛 Hozirgi vaqt: {hour:02d}:{minutes:02d}"
    await call_back.answer(text=text, show_alert=True)


async def handle_cancel(call_back: CallbackQuery, state: FSMContext):
    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    await state.set_state(BotState.WORKER_MENU)
    kb = WORKER_MENU  # reply_markup for workers
    await call_back.message.edit_text(text=text, reply_markup=kb)


async def call_accept_handle(call_back: CallbackQuery, state: FSMContext):
    pass


async def handle_time(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    parts = call_back.data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])
    await call_back.message.edit_reply_markup(
        reply_markup=time_keyboard(hour=hour, minutes=minutes)
    )


@router.callback_query(F.data, BotState.SET_START)
async def call_time_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data

    if data.startswith("accept_"):
        await call_accept_handle(call_back, state)
        return
    elif data.startswith("now_"):
        await handle_current(call_back, state)
        return

    match data:
        case "cancel":
            await handle_cancel(call_back, state)
        case _:
            await handle_time(call_back, state)
