import logging
from sqlalchemy.ext.asyncio import AsyncSession

from .load import BotLoader

log = logging.getLogger(__name__)


class AdminUtil:
    @staticmethod
    async def send_message_to_admins(session: AsyncSession, text: str, admins: list):
        bot = await BotLoader.get_bot()

        for admin in admins:
            try:
                await bot.send_message(chat_id=admin.tg_id, text=text)
            except Exception as e:
                logging.warning(f"Message to admin {admin.name} failed: {e}")
        return text

    @staticmethod
    async def send_msg(chat_id: int, msg: str):
        bot = await BotLoader.get_bot()
        try:
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.warning(f"Message to {chat_id} failed: {e}")
