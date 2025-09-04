import logging

from core.config import settings
from db import db_helper
from db.crud import user_crud

from .load import BotLoader

log = logging.getLogger(__name__)


class AdminUtil:
    @staticmethod
    async def send_message_to_admins(text: str):
        bot = BotLoader.get_bot()

        async with db_helper.session_factory() as session:
            admins = await user_crud.read_all(
                session=session, filters={"is_superuser": True}
            )

        for admin in admins:
            try:
                await bot.send_message(chat_id=admin.tg_id, text=text)
            except Exception as e:
                logging.warning(f"Message to admin {admin.name} failed: {e}")
        return text

    @staticmethod
    async def send_msg(chat_id: int, msg: str):
        bot = BotLoader.get_bot()
        try:
            await bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.warning(f"Message to {chat_id} failed: {e}")
