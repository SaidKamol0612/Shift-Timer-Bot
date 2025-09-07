from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db.models import User


def workers_kb(models: list[User]):
    kb = ReplyKeyboardBuilder()
    for model in models:
        kb.add(KeyboardButton(text=model.name))
    kb.add(KeyboardButton(text="❌ Bekor qilish"))
    return kb.adjust(1).as_markup(resize_keyboard=True)
