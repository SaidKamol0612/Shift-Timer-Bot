__all__ = ("router",)

from aiogram import Router

# Import the sub-router from handler
from .admin import router as admin_router
from .worker import router as worker_router

# Initialize main router
router = Router()
router.include_router(admin_router)
router.include_router(worker_router)
