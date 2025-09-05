from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import date as PyDate

from keyboards.inline import count_keyboard, WORKER_MENU, roles_keyboard
from states import BotState
from db import db_helper
from db.crud import user_crud, role_crud, shift_report_crud, shift_role_crud
from db.schemas import ShiftReportSchema, ShiftRoleSchema
from utils import AdminUtil

router = Router()


@router.callback_query(F.data == "night_shift", BotState.WORKER_MENU)
async def call_day_shift_handle(call_back: CallbackQuery, state: FSMContext):
    today = PyDate.today()
    text = (
        f"<b>📅 Sana:</b> {today}\n"
        "<b>Smena:</b> 🌙 Tungi\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida nechta xamir tayyorlaganingizni tanlang.</b>"
    )
    await state.update_data(date=today)
    await state.set_state(BotState.SetNightShift.SET_COUNT)
    await call_back.message.delete()
    await call_back.message.answer(text=text, reply_markup=count_keyboard(current=10))


@router.callback_query(F.data == ("cancel"))
async def cancel(call_back: CallbackQuery, state: FSMContext):
    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    await state.set_state(BotState.WORKER_MENU)
    kb = WORKER_MENU  # reply_markup for workers
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
        reply_markup=count_keyboard(current=current)
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
    await call_back.message.edit_text(text=text, reply_markup=roles_keyboard())


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
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"🔢 <b>{count}</b> ta xamir qorilgan.\n"
        f"{roles}\n"
        "\n<b>Iltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.</b>"
    )
    await state.set_state(BotState.SetNightShift.SET_ROLES)
    await call_back.message.edit_text(
        text=text, reply_markup=roles_keyboard(used_roles=used_roles)
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
        admins = await user_crud.read_all(
            session=session, filters={"is_superuser": True}
        )
        sh = await shift_report_crud.create(
            session=session,
            schema=ShiftReportSchema(
                user_id=current_user.id,
                date=date,
                count_dough=int(count),
                shift_type="night",
            ),
        )
        for r in used_roles:
            role = await role_crud.read(session=session, filters={"code": r[0].upper()})
            await shift_role_crud.create(
                session=session,
                schema=ShiftRoleSchema(
                    date=date,
                    role_id=role.id,
                    shift_id=sh.id,
                    is_approved=False,
                ),
            )

    roles = " ".join([role.title() for role in used_roles])
    text = (
        f"Ishchi: {current_user.name}"
        f"<b>📅 Sana:</b> {date}\n"
        "<b>Smena:</b> ☀️ Kunduzgi\n"
        f"🔢 <b>{count}</b> ta xamir qorilgan.\n\n"
        f"{roles}\n"
    )

    await call_back.message.edit_text(
        text=call_back.message.text.replace(
            "\n\nIltimos, endi pastdagi tugmalar yordamida qanday ishlarda ishlaganingizni tanlang.",
            " ",
        ),
        reply_markup=None,
    )
    # TODO: add accepting report logic for admins
    await AdminUtil.send_message_to_admins(session=session, text=text, admins=admins)
    await call_back.message.answer(text="✅ Qabul qilindi.")

    await state.set_state(BotState.WORKER_MENU)
    await call_back.message.answer(
        text="💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin.",
        reply_markup=WORKER_MENU,
    )
