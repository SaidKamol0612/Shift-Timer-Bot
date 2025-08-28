import asyncio
from typing import Optional
from aiogram import Bot
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


class BotLoader:
    """
    Singleton loader for Aiogram Bot instance.

    Token is required only on first initialization.
    Subsequent calls to get_bot() will return the same instance without token.
    """

    _bot: Optional[Bot] = None
    _token: Optional[str] = None
    _lock = asyncio.Lock()

    @classmethod
    async def init_bot(cls, token: str, use_html: bool = True) -> Bot:
        """
        Initialize bot explicitly (should be called once on startup).

        Args:
            token (str): Telegram bot token.
            use_html (bool): If True — use HTML parse mode, else MarkdownV2.

        Returns:
            Bot: Aiogram bot instance.
        """
        async with cls._lock:
            if cls._bot is None:
                cls._token = token
                cls._bot = Bot(
                    token=token,
                    default=DefaultBotProperties(
                        parse_mode=ParseMode.HTML if use_html else ParseMode.MARKDOWN_V2
                    ),
                )
        return cls._bot

    @classmethod
    async def get_bot(cls) -> Bot:
        """
        Get bot instance after it has been initialized.

        Raises:
            RuntimeError: If bot has not been initialized yet.

        Returns:
            Bot: Aiogram bot instance.
        """
        if cls._bot is None:
            raise RuntimeError("Bot is not initialized. Call init_bot(token) first.")
        return cls._bot

    @staticmethod
    async def set_bot_commands(bot: Bot, new_commands: dict[str, str]) -> None:
        """
        Set bot commands visible in Telegram menu.

        Args:
            bot (Bot): Aiogram bot instance.
            new_commands (dict[str, str]): Mapping {command: description}.
        """
        commands = [BotCommand(command=c, description=d) for c, d in new_commands.items()]
        await bot.set_my_commands(commands)

    @classmethod
    async def close_bot(cls) -> None:
        """
        Close bot session and clear singleton instance.
        Should be called on application shutdown.
        """
        if cls._bot:
            await cls._bot.session.close()
            cls._bot = None
            cls._token = None
