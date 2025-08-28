# -------------------------------
# Expose only 'router' from this module
# -------------------------------
__all__ = ("router",)

from aiogram import Router
from middlewares.chat_type import PrivateChatOnlyMiddleware

# Import the sub-router from handler
from .handler import router as r

# -------------------------------
# Initialize main personal router
# -------------------------------
router = Router()

# -------------------------------
# Initialize middleware to restrict commands to private chats
# -------------------------------
private_only = PrivateChatOnlyMiddleware()

# Apply middleware to message and callback_query handlers
router.message.middleware(private_only)
router.callback_query.middleware(private_only)

# -------------------------------
# Include sub-router with actual handlers
# -------------------------------
router.include_router(r)
