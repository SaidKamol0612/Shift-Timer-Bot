import logging
from random import choice

from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from handlers import router as main_router
from utils import BotLoader
from core.config import settings
from states.bot_state import BotState

# -------------------------------
# Initialize dispatcher with in-memory FSM storage
# -------------------------------
dp = Dispatcher(storage=MemoryStorage())

# -------------------------------
# Logger for this module
# -------------------------------
log = logging.getLogger(__name__)

# List of emojis for random reaction to /start
emojies = ["👍", "❤️", "🔥", "🥰", "👏", "😁", "🎉", "🤩", "👌", "😍"]


# -------------------------------
# Bot startup function
# -------------------------------
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


# -------------------------------
# /start command handler
# -------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command:
    - React with a random emoji
    - Greet the user personally
    """
    await message.react([ReactionTypeEmoji(emoji=choice(emojies))])

    user = message.from_user
    user_link = f"tg://user?id={user.id}"

    log.info("%s started bot", user.first_name or user.username)
    start_msg = (
        f"👋 Assalomu alaykum <a href='{user_link}'>"
        f"{user.first_name}</a>, botimizga xush kelibsiz\n\n"
    )

    await state.set_state(BotState.START)
    await message.reply(text=start_msg)
