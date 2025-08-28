from aiogram.types import Message
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable


class PrivateChatOnlyMiddleware(BaseMiddleware):
    """
    Middleware to restrict command usage to private chats only.
    Sends a warning message if the command is used in a group or channel.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Check if chat type is private
        if event.chat.type != "private":
            await event.answer(
                "⚠️ Bu buyruq faqat shaxsiy suhbatda ishlaydi."
            )  # Warning message
            return  # Stop processing
        # Continue to handler if in private chat
        return await handler(event, data)


class GroupChannelChatOnlyMiddleware(BaseMiddleware):
    """
    Middleware to restrict command usage to groups, supergroups, or channels.
    Sends a warning message if the command is used in a private chat.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        # Check if chat type is group, supergroup, or channel
        if event.chat.type not in ("group", "supergroup", "channel"):
            await event.answer(
                "⚠️ Bu buyruq faqat guruhlarda ishlaydi."
            )  # Warning message
            return  # Stop processing
        # Continue to handler if in group/channel
        return await handler(event, data)
