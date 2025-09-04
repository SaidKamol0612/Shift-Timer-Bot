from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date

from states.bot_state import BotState
from keyboards.inline import (
    time_keyboard,
    WORKER_MENU,
    duration_keyboard,
    roles_keyboard,
    ACCEPT_OR_NO,
)
from db import db_helper
from db.crud import user_crud
from utils import AdminUtil

# Initialize router
router = Router()


@router.callback_query(F.data == "day_shift", BotState.WORKER_MENU)
async def call_day_shift_handle(call_back: CallbackQuery, state: FSMContext):
    today = date.today()
    text = (
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida ish boshlagan vaqtingizni tanlang.</b>"
    )
    await state.update_data(date=today)
    await state.set_state(BotState.SetDayShift.SET_START)
    await call_back.message.edit_text(text=text, reply_markup=time_keyboard())


async def handle_cancel(call_back: CallbackQuery, state: FSMContext):
    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    await state.set_state(BotState.WORKER_MENU)
    kb = WORKER_MENU  # reply_markup for workers
    await call_back.message.edit_text(text=text, reply_markup=kb)


async def show_current_time(call_back: CallbackQuery, state: FSMContext):
    parts = call_back.data.split("_")[1].split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])
    text = f"🕛 Hozirgi vaqt: {hour:02d}:{minutes:02d}"
    await call_back.answer(text=text, show_alert=True)


async def handle_time_pm(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    parts = call_back.data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])
    await call_back.message.edit_reply_markup(
        reply_markup=time_keyboard(hour=hour, minutes=minutes)
    )


async def call_accept_start_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    time_data = call_back.data.split("_")[1]
    parts = time_data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])

    await state.update_data(start_hour=hour)
    await state.update_data(start_minutes=minutes)
    await state.set_state(BotState.SetDayShift.SET_END)

    date = (await state.get_data()).get("date")
    text = (
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{hour:02d}:{minutes:02d}</b> da boshlandi.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida ish tugatgan vaqtingizni tanlang.</b>"
    )
    await state.update_data(date=date)
    await state.set_state(BotState.SetDayShift.SET_END)
    await call_back.message.edit_text(
        text=text, reply_markup=time_keyboard(hour=hour, minutes=minutes)
    )


async def call_accept_night_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    time_data = call_back.data.split("_")[1]
    parts = time_data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])

    await state.update_data(end_hour=hour)
    await state.update_data(end_minutes=minutes)

    today = (await state.get_data()).get("today")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")

    text = (
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{hour:02d}:{minutes:02d}</b> da tugatildi.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida tanafus olgan vaqtingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetDayShift.SET_PAUSE)
    await call_back.message.edit_text(text=text, reply_markup=duration_keyboard())


async def call_accept_duration_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    time_data = call_back.data.split("_")[1]
    parts = time_data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])

    await state.update_data(pause_hour=hour)
    await state.update_data(pause_minutes=minutes)

    today = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")
    end_hour = (await state.get_data()).get("end_hour")
    end_minutes = (await state.get_data()).get("end_minutes")

    text = (
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{end_hour:02d}:{end_minutes:02d}</b> da tugatildi.\n"
        f"⏸️ Tanafus olingan vaqt: <b>{hour:02d}:{minutes:02d}</b>.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida nima ish qilganingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetDayShift.SET_ROLE)
    await call_back.message.edit_text(text=text, reply_markup=roles_keyboard())


@router.callback_query(F.data.startswith("role_"), BotState.SetDayShift.SET_ROLE)
async def call_accept_role_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    role = call_back.data.split("_")[1]

    await state.update_data(role=role)

    today = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")
    end_hour = (await state.get_data()).get("end_hour")
    end_minutes = (await state.get_data()).get("end_minutes")
    pause_hour = (await state.get_data()).get("pause_hour")
    pause_minutes = (await state.get_data()).get("pause_minutes")

    text = (
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{end_hour:02d}:{end_minutes:02d}</b> da tugatildi.\n"
        f"⏸️ Tanafus olingan vaqt: <b>{pause_hour:02d}:{pause_minutes:02d}</b>.\n"
        f"{role.title()}\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida nima ish qilganingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetDayShift.ACCEPT)
    await call_back.message.edit_text(text=text, reply_markup=ACCEPT_OR_NO)


async def accept_shift_role(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    user = call_back.from_user
    role = call_back.data.split("_")[1]

    today = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")
    end_hour = (await state.get_data()).get("end_hour")
    end_minutes = (await state.get_data()).get("end_minutes")
    pause_hour = (await state.get_data()).get("pause_hour")
    pause_minutes = (await state.get_data()).get("pause_minutes")
    role = (await state.get_data()).get("role")

    async with db_helper.session_factory() as session:
        current_user = await user_crud.read(session=session, filters={"tg_id": user.id})

    text = (
        f"Ishchi: {current_user.name}"
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{end_hour:02d}:{end_minutes:02d}</b> da tugatildi.\n"
        f"⏸️ Tanafus olingan vaqt: <b>{pause_hour:02d}:{pause_minutes:02d}</b>.\n"
        f"{role.title()}\n"
    )
    # TODO: add accepting report logic for admins 
    await AdminUtil.send_message_to_admins(text=text)
    await call_back.message.edit_text(
        text="✅ Qabul qilindi."
    )

    await state.set_state(BotState.WORKER_MENU)
    await call_back.message.edit_text(
        text="💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin.",
        reply_markup=WORKER_MENU,
    )


@router.callback_query(F.data, BotState.SetDayShift.SET_START)
async def call_time_start_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_"):
        await call_accept_start_handle(call_back, state)
    elif data.startswith("now_"):
        await show_current_time(call_back, state)
    elif data == "cancel":
        await handle_cancel(call_back, state)
    else:
        await handle_time_pm(call_back, state)


@router.callback_query(F.data, BotState.SetDayShift.SET_END)
async def call_time_end_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_"):
        await call_accept_night_handle(call_back, state)
    elif data.startswith("now_"):
        await show_current_time(call_back, state)
    elif data == "cancel":
        await handle_cancel(call_back, state)
    else:
        await handle_time_pm(call_back, state)


@router.callback_query(F.data, BotState.SetDayShift.SET_PAUSE)
async def call_time_pause_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_"):
        await call_accept_duration_handle(call_back, state)
    elif data.startswith("pause_"):
        await show_current_time(call_back, state)
    elif data == "cancel":
        await handle_cancel(call_back, state)
    else:
        await handle_time_pm(call_back, state)


@router.callback_query(F.data, BotState.SetDayShift.ACCEPT)
async def call_time_pause_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_shift_report"):
        (call_back, state)
    elif data == "cancel":
        await handle_cancel(call_back, state)
