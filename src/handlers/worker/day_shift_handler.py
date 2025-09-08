from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date as PyDate

from states.bot_state import BotState
from keyboards.inline import InlineKeyboards
from db import db_helper
from db.crud import user_crud, shift_crud, shift_role_crud
from services import role_service
from db.schemas import ShiftSchema, ShiftRoleSchema
from utils import AdminUtil
from core.enums import ShiftTypeENUM

# Initialize router
router = Router()


@router.callback_query(F.data == "day_shift", BotState.WORKER_MENU)
async def call_day_shift_handle(call_back: CallbackQuery, state: FSMContext):
    async with db_helper.session_factory() as session:
        curr = await user_crud.read(
            session=session, filters={"tg_id": call_back.from_user.id}
        )
        sh = await shift_crud.read(
            session=session,
            filters={
                "user_id": curr.id,
                "shift_type": "day",
                "date": PyDate.today(),
                "is_approved": True,
            },
        )
    if sh:
        text = "⚠️ Siz bugun, kunduzgi smena uchun hisobot kiritib bo'lgansiz va boshqa kirita olmaysiz."
        await call_back.answer(text=text, show_alert=True)
        return

    today = PyDate.today()
    text = (
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida ish boshlagan vaqtingizni tanlang.</b>"
    )
    await state.update_data(date=today)
    await state.set_state(BotState.SetDayShift.SET_START)
    await call_back.message.delete()
    await call_back.message.answer(
        text=text, reply_markup=InlineKeyboards.Pickers.time_picker_kb()
    )


@router.callback_query(F.data, BotState.SetDayShift.SET_START)
async def call_time_start_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_"):
        await call_accept_start_handle(call_back, state)
    elif data.startswith("now_"):
        await show_current_time(call_back, state)
    elif data == "cancel":
        await cancel(call_back, state)
    else:
        await handle_time_pm(call_back, state)


@router.callback_query(F.data, BotState.SetDayShift.SET_END)
async def call_time_end_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_"):
        await call_accept_end_handle(call_back, state)
    elif data.startswith("now_"):
        await show_current_time(call_back, state)
    elif data == "cancel":
        await cancel(call_back, state)
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
        await cancel(call_back, state)
    else:
        await handle_time_pm(call_back, state)


@router.callback_query(F.data == ("cancel"))
async def cancel(call_back: CallbackQuery, state: FSMContext):
    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    await state.set_state(BotState.WORKER_MENU)
    kb = InlineKeyboards.Menus.worker_menu()  # reply_markup for workers
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

    start_hour = (await state.get_data()).get("start_hour", 6)
    start_minutes = (await state.get_data()).get("start_minutes", 0)

    await call_back.message.edit_reply_markup(
        reply_markup=InlineKeyboards.Pickers.time_picker_kb(
            hour=hour,
            minutes=minutes,
            min_hour=(start_hour + 1),
            max_minutes=(start_minutes),
        )
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
        "Sizning ish kuningiz bo'yicha hisobot.\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{hour:02d}:{minutes:02d}</b> da boshlandi.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida ish tugatgan vaqtingizni tanlang.</b>"
    )
    await state.update_data(date=date)
    await state.set_state(BotState.SetDayShift.SET_END)
    await call_back.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.Pickers.time_picker_kb(
            hour=18 if hour == 8 else hour + 1,
            minutes=minutes,
            min_hour=hour + 1,
            max_minutes=minutes,
        ),
    )


async def call_accept_end_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    time_data = call_back.data.split("_")[1]
    parts = time_data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])

    await state.update_data(end_hour=hour)
    await state.update_data(end_minutes=minutes)

    date = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")

    text = (
        "Sizning ish kuningiz bo'yicha hisobot.\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{hour:02d}:{minutes:02d}</b> da tugatildi.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida tanafus olgan vaqtingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetDayShift.SET_PAUSE)
    await call_back.message.edit_text(
        text=text, reply_markup=InlineKeyboards.Pickers.duration_picker_kb()
    )


async def call_accept_duration_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    time_data = call_back.data.split("_")[1]
    parts = time_data.split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])

    await state.update_data(pause_hour=hour)
    await state.update_data(pause_minutes=minutes)

    date = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")
    end_hour = (await state.get_data()).get("end_hour")
    end_minutes = (await state.get_data()).get("end_minutes")

    text = (
        "Sizning ish kuningiz bo'yicha hisobot.\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{end_hour:02d}:{end_minutes:02d}</b> da tugatildi.\n"
        f"⏸️ Tanafus olingan vaqt: <b>{hour:02d}:{minutes:02d}</b>.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetDayShift.SET_ROLES)
    await call_back.message.edit_text(
        text=text, reply_markup=InlineKeyboards.Shift.roles_keyboard()
    )


@router.callback_query(F.data.startswith("role_"), BotState.SetDayShift.SET_ROLES)
async def call_accept_role_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    role = call_back.data.split("_")[1]

    used_roles: list = (await state.get_data()).get("roles", [])
    if role in used_roles:
        used_roles.remove(role)
    else:
        used_roles.append(role)
    await state.update_data(roles=used_roles)

    date = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minutes = (await state.get_data()).get("start_minutes")
    end_hour = (await state.get_data()).get("end_hour")
    end_minutes = (await state.get_data()).get("end_minutes")
    pause_hour = (await state.get_data()).get("pause_hour")
    pause_minutes = (await state.get_data()).get("pause_minutes")

    roles = " ".join([role.title() for role in used_roles])
    text = (
        "Sizning ish kuningiz bo'yicha hisobot.\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minutes:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{end_hour:02d}:{end_minutes:02d}</b> da tugatildi.\n"
        f"⏸️ Tanafus olingan vaqt: <b>{pause_hour:02d}:{pause_minutes:02d}</b>.\n"
        f"{roles}\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetDayShift.SET_ROLES)
    await call_back.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.Shift.roles_keyboard(used_roles=used_roles),
    )


@router.callback_query(
    F.data == ("accept_shift_report"), BotState.SetDayShift.SET_ROLES
)
async def accept_shift_role(call_back: CallbackQuery, state: FSMContext):
    used_roles: list[str] = (await state.get_data()).get("roles")
    if not used_roles:
        await call_back.answer(
            "⚠️ Xattolik. Avval nima ishlar bilan shug'ulangangizni belgilang.",
            show_alert=True,
        )
        return

    await call_back.answer("⌛ Sizning hisobotingiz adminlarga yuborilmoqda...")

    user = call_back.from_user
    date = (await state.get_data()).get("date")
    start_hour = (await state.get_data()).get("start_hour")
    start_minute = (await state.get_data()).get("start_minutes")
    end_hour = (await state.get_data()).get("end_hour")
    end_minute = (await state.get_data()).get("end_minutes")
    pause_hours = (await state.get_data()).get("pause_hour")
    pause_minutes = (await state.get_data()).get("pause_minutes")

    async with db_helper.session_factory() as session:
        current_user = await user_crud.read(session=session, filters={"tg_id": user.id})
        admin = await user_crud.read(session=session, filters={"is_superuser": True})
        sh = await shift_crud.create(
            session=session,
            schema=ShiftSchema(
                user_id=current_user.id,
                date=date,
                start_hour=int(start_hour),
                start_minute=int(start_minute),
                end_hour=int(end_hour),
                end_minute=int(end_minute),
                pause_hours=int(pause_hours),
                pause_minutes=int(pause_minutes),
                shift_type=ShiftTypeENUM.DAY,
            ),
        )

        daily = 0
        for r in used_roles:
            role = role_service.read_role(code=r[0])
            await shift_role_crud.create(
                session=session,
                schema=ShiftRoleSchema(
                    date=date,
                    role_code=role.code,
                    shift_id=sh.id,
                ),
            )
            daily += role.day_rate_for_hour * sh.work_duration_hours

    roles = " ".join([role.title() for role in used_roles])
    text = (
        f"Ishchi: {current_user.name}"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"▶️ Ish <b>{start_hour:02d}:{start_minute:02d}</b> da boshlandi.\n"
        f"⏹️ Ish <b>{end_hour:02d}:{end_minute:02d}</b> da tugatildi.\n"
        f"⏸️ <b>{pause_hours:02d}:{pause_minutes:02d}</b> tanafus olindi.\n"
        f"{roles}\n"
        f"\n<b>Jami:</b> {daily}\n"
    )

    await call_back.message.edit_text(
        text=call_back.message.text.replace(
            "\n\nIltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.",
            f"\n<b>Jami:</b> {daily}\n",
        ),
        reply_markup=None,
    )
    await AdminUtil.send_report_to_admin(
        text=text,
        reply_markup=InlineKeyboards.Shift.approve_or_cancel_shift_kb(sh.id),
        admin=admin,
    )

    await state.set_state(BotState.WORKER_MENU)
    await call_back.message.answer(
        text="💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin.",
        reply_markup=InlineKeyboards.Menus.worker_menu(),
    )
