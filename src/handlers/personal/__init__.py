__all__ = ("router",)

from aiogram import Router
from middlewares.chat_type import PrivateChatOnlyMiddleware

# Import the sub-router from handler
from .handler import router as r

# Initialize main personal router
router = Router()

# Initialize middleware to restrict commands to private chats
private_only = PrivateChatOnlyMiddleware()

# Apply middleware to message handlers
router.message.middleware(private_only)

router.include_router(r)
