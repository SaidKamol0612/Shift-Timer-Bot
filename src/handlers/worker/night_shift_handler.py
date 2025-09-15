from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date as PyDate

from keyboards.inline import InlineKeyboards
from states import BotState
from db import db_helper
from db.crud import user_crud, shift_crud, shift_role_crud
from services import role_service
from db.schemas import ShiftSchema, ShiftRoleSchema
from utils import AdminUtil
from core.enums import ShiftTypeENUM

router = Router()


@router.callback_query(F.data == "night_shift", BotState.WORKER_MENU)
async def call_day_shift_handle(call_back: CallbackQuery, state: FSMContext):
    async with db_helper.session_factory() as session:
        curr = await user_crud.read(
            session=session, filters={"tg_id": call_back.from_user.id}
        )
        sh = await shift_crud.read(
            session=session,
            filters={
                "user_id": curr.id,
                "shift_type": "NIGHT",
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
        "<b>Smena:</b> 🌙 Tungi\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida nechta xamir tayyorlaganingizni tanlang.</b>"
    )
    await state.update_data(date=today)
    await state.set_state(BotState.SetNightShift.SET_COUNT)
    await call_back.message.delete()
    await call_back.message.answer(
        text=text, reply_markup=InlineKeyboards.Pickers.count_picker_kb(current=8)
    )


@router.callback_query(F.data == ("cancel"))
async def cancel(call_back: CallbackQuery, state: FSMContext):
    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    await state.set_state(BotState.WORKER_MENU)
    kb = InlineKeyboards.Menus.worker_menu()  # reply_markup for workers
    await call_back.message.edit_text(text=text, reply_markup=kb)


@router.callback_query(F.data, BotState.SetNightShift.SET_COUNT)
async def call_time_start_handle(call_back: CallbackQuery, state: FSMContext):
    data = call_back.data
    if data.startswith("accept_"):
        await call_accept_count_handle(call_back, state)
    elif data.startswith("count_"):
        await show_current(call_back, state)
    elif data == "cancel":
        await cancel(call_back, state)
    else:
        await handle_count_pm(call_back, state)


async def show_current(call_back: CallbackQuery, state: FSMContext):
    parts = call_back.data.split("_")[1].split(":")  # format: HH:MM
    hour = int(parts[0])
    minutes = int(parts[1])
    text = f"🔢 Hozirgi hisob: {hour:02d}:{minutes:02d}"
    await call_back.answer(text=text, show_alert=True)


async def handle_count_pm(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    current = int(call_back.data)

    await call_back.message.edit_reply_markup(
        reply_markup=InlineKeyboards.Pickers.count_picker_kb(current=current)
    )


async def call_accept_count_handle(call_back: CallbackQuery, state: FSMContext):
    await call_back.answer()
    parts = call_back.data.split("_")
    count = parts[1]

    await state.update_data(count=count)
    await state.set_state(BotState.SetNightShift.SET_ROLES)

    date = (await state.get_data()).get("date")
    text = (
        "Sizning ish kuningiz bo'yicha hisobot.\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> 🌙 Tungi\n"
        f"🔢 <b>{count}</b> ta xamir qorilgan.\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.</b>"
    )
    await call_back.message.edit_text(
        text=text, reply_markup=InlineKeyboards.Shift.roles_keyboard()
    )


@router.callback_query(F.data.startswith("role_"), BotState.SetNightShift.SET_ROLES)
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
    count = (await state.get_data()).get("count")

    roles = " ".join([role.title() for role in used_roles])
    text = (
        "Sizning ish kuningiz bo'yicha hisobot.\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> 🌙 Tungi\n"
        f"🔢 <b>{count}</b> ta xamir qorilgan.\n"
        f"{roles}\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetNightShift.SET_ROLES)
    await call_back.message.edit_text(
        text=text,
        reply_markup=InlineKeyboards.Shift.roles_keyboard(used_roles=used_roles),
    )


@router.callback_query(
    F.data == ("accept_shift_report"), BotState.SetNightShift.SET_ROLES
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
    count = (await state.get_data()).get("count")

    async with db_helper.session_factory() as session:
        current_user = await user_crud.read(session=session, filters={"tg_id": user.id})
        admin = await user_crud.read(session=session, filters={"is_superuser": True})
        sh = await shift_crud.create(
            session=session,
            schema=ShiftSchema(
                user_id=current_user.id,
                date=date,
                count_dough=int(count),
                shift_type=ShiftTypeENUM.NIGHT,
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
            daily += role.night_rate_for_dough * sh.count_dough

    roles = " ".join([role.title() for role in used_roles])
    text = (
        f"Ishchi: {current_user.name}\n"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> 🌙 Tungi\n"
        f"🔢 <b>{count}</b> ta xamir qorilgan.\n\n"
        f"{roles}\n"
        f"<b>Jami:</b> {daily}\n"
    )

    await call_back.message.edit_text(
        text=call_back.message.text.replace(
            "\n\nIltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.",
            f"\n<b>Jami:</b> {daily}",
        ),
        reply_markup=None,
    )
    await AdminUtil.send_report_to_admin(
        text=text,
        reply_markup=InlineKeyboards.Shift.approve_or_cancel_shift_kb(shift_id=sh.id),
        admin=admin,
    )

    await state.set_state(BotState.WORKER_MENU)
    await call_back.message.answer(
        text="💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin.",
        reply_markup=InlineKeyboards.Menus.worker_menu(),
    )
