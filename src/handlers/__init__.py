__all__ = ("router",)

from aiogram import Router

# Import the sub-router from handler
from .personal import router as personal_router

# Initialize main router
router = Router()
router.include_router(personal_router)
