__all__ = ("router",)

from aiogram import Router

from .approve_handler import router as approve_router
from .payment_handler import router as payment_router

router = Router()
router.include_router(approve_router)
router.include_router(payment_router)
