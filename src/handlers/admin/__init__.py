__all__ = (
    "router",
)

from aiogram import Router

from .approve_handler import router as approve_router

router = Router()
router.include_router(approve_router)