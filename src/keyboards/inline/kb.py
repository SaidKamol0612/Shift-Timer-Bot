from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional

from core.enums import Roles

WORKER_MENU = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="☀️ Kunduzgi / День", callback_data="day_shift"),
            InlineKeyboardButton(text="🌙 Tungi / Ночь", callback_data="night_shift"),
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

ACCEPT_OR_NO = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Adminga jo'natish", callback_data="accept_shift_report"
            ),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"),
        ],
    ]
)


def time_keyboard(hour: Optional[int] = 9, minutes: Optional[int] = 0):
    now = f"{hour:02d}:{minutes:02d}"

    # Limits:
    if now == "07:00":
        minus = "19:00"  # turn to evening
        plus = "07:30"  # normal plus
    elif now == "19:00":
        minus = "18:30"  # normal minus
        plus = "07:00"  # turn to morning
    else:
        # universal calculate +30/-30 with wrapping 24 hours around
        def shift_time(h, m, delta):
            total_minutes = (h * 60 + m + delta) % (24 * 60)
            new_h = total_minutes // 60
            new_m = total_minutes % 60
            return f"{new_h:02d}:{new_m:02d}"

        minus = shift_time(hour, minutes, -30)
        plus = shift_time(hour, minutes, +30)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="-", callback_data=minus),
                InlineKeyboardButton(text=now, callback_data=f"now_{now}"),
                InlineKeyboardButton(text="+", callback_data=plus),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"),
                InlineKeyboardButton(text="✅ Tayyor", callback_data=f"accept_{now}"),
            ],
        ]
    )
    return kb


def duration_keyboard(hour: Optional[int] = 0, minutes: Optional[int] = 0):
    duration = f"{hour:02d}:{minutes:02d}"

    # Limits:
    if duration == "00:00":
        minus = "12:00"  # turn to 12 hour
        plus = "00:30"  # normal plus
    elif duration == "12:00":
        minus = "11:30"  # normal minus
        plus = "00:00"  # turn to 0 hour
    else:
        # universal calculate +30/-30 with wrapping 24 hours around
        def wrap(h, m, delta):
            total_minutes = (h * 60 + m + delta) % (24 * 60)
            new_h = total_minutes // 60
            new_m = total_minutes % 60
            return f"{new_h:02d}:{new_m:02d}"

        minus = wrap(hour, minutes, -30)
        plus = wrap(hour, minutes, +30)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="-", callback_data=minus),
                InlineKeyboardButton(text=duration, callback_data=f"pause_{duration}"),
                InlineKeyboardButton(text="+", callback_data=plus),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"),
                InlineKeyboardButton(
                    text="✅ Tayyor", callback_data=f"accept_{duration}"
                ),
            ],
        ]
    )
    return kb


def roles_keyboard():
    kb = InlineKeyboardBuilder()
    for role in Roles:
        kb.add(
            InlineKeyboardButton(text=role.title(), callback_data=f"role_{role.name}")
        )
    return kb.adjust(2).as_markup()
