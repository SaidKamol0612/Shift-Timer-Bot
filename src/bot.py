import logging

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from handlers import router as main_router
from utils import BotLoader
from core.config import settings
from states.bot_state import BotState
from db import db_helper
from db.crud import user_crud
from db.schemas import UserSchema
from keyboards.inline import InlineKeyboards

# Initialize dispatcher with in-memory FSM storage
dp = Dispatcher(storage=MemoryStorage())

# Logger for this module
log = logging.getLogger(__name__)


# Bot startup function
async def start_bot() -> None:
    """
    Initialize bot instance, include router, and start polling.
    """

    # Initialize Bot using BotLoader
    bot = await BotLoader.init_bot(settings.bot.token)

    # Register all handlers from main router
    dp.include_router(main_router)

    # Start polling
    await dp.start_polling(bot)


# /start command handler
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command:
    - Greet the user personally
    """

    user = message.from_user
    async with db_helper.session_factory() as session:
        current_user = await user_crud.read(session=session, filters={"tg_id": user.id})
    user_link = f"tg://user?id={user.id}"
    text = (
        f"👋 Assalomu alaykum <a href='{user_link}'>"
        f"{current_user.name if current_user else user.first_name}</a>, botimizga xush kelibsiz\n\n"
    )
    if current_user:
        text += "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
        if current_user.is_superuser:
            kb = InlineKeyboards.Menus.admin_menu()  # reply_markup for admins
            await state.set_state(BotState.ADMIN_MENU)
        else:
            kb = InlineKeyboards.Menus.worker_menu()  # reply_markup for workers
            await state.set_state(BotState.WORKER_MENU)
    else:
        text += (
            "ℹ️ Botimizdan foydalanishdan oldin botga <b>o'z ismingizni</b> yuboring."
        )
        await state.set_state(BotState.Register.GET_NAME)
        kb = None

    log.info("%s started bot", user.first_name or user.username)
    await message.reply(text=text, reply_markup=kb)


@dp.message(F.text, BotState.Register.GET_NAME)
async def reg_name(message: Message, state: FSMContext):
    name = message.text.strip()
    user = message.from_user
    async with db_helper.session_factory() as session:
        current_user = await user_crud.create(
            session=session,
            schema=UserSchema(
                tg_id=user.id,
                name=name,
            ),
        )

    text = "💡 Pastdagi tugmalarni bosib foydalanishingiz mumkin."
    if current_user.is_superuser:
        await state.set_state(BotState.ADMIN_MENU)
        kb = InlineKeyboards.Menus.admin_menu()  # reply_markup for admins
    else:
        await state.set_state(BotState.WORKER_MENU)
        kb = InlineKeyboards.Menus.worker_menu()  # reply_markup for workers
    await message.answer(text=text, reply_markup=kb)
