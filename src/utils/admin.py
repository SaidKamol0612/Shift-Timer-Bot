import logging
from aiogram.types import InlineKeyboardMarkup

from .load import BotLoader

log = logging.getLogger(__name__)


class AdminUtil:
    @staticmethod
    async def send_report_to_admin(
        text: str, reply_markup: InlineKeyboardMarkup, admin=None
    ):
        if admin:
            bot = await BotLoader.get_bot()
            try:
                await bot.send_message(
                    chat_id=admin.tg_id, text=text, reply_markup=reply_markup
                )
            except Exception as e:
                logging.warning(f"Message to admin {admin.name} failed: {e}")

    @staticmethod
    async def send_msg(chat_id: int, msg: str):
        bot = await BotLoader.get_bot()
        try:
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.warning(f"Message to {chat_id} failed: {e}")
