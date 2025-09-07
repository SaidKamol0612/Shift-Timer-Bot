__all__ = ("router",)

from aiogram import Router
from middlewares.chat_type import PrivateChatOnlyMiddleware

# Import the sub-router from handler
from .day_shift_handler import router as day_shift_router
from .night_shift_handler import router as night_shift_router
from .report_handler import router as report_router

# Initialize main personal router
router = Router()

# Initialize middleware to restrict commands to private chats
private_only = PrivateChatOnlyMiddleware()

# Apply middleware to message handlers
router.message.middleware(private_only)

router.include_router(day_shift_router)
router.include_router(night_shift_router)
router.include_router(report_router)
