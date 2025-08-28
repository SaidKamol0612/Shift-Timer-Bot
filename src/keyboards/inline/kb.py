from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

WORKER_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="☀️ Kunduzgi / День", callback_data="day_shift"),
            InlineKeyboardButton(text="🌙 Tungi / День", callback_data="night_shift"),
        ],
        [InlineKeyboardButton(text="📃 Hisobot", callback_data="report")],
    ]
)

ADMIN_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 To'lov amalga oshirish", callback_data="pay")],
        [InlineKeyboardButton(text="📃 Hisobot", callback_data="report")],
    ]
)
