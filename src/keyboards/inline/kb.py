from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional

from core.enums import RoleENUM


class InlineKeyboards:
    class Menus:
        @staticmethod
        def worker_menu() -> InlineKeyboardMarkup:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="☀️ Kunduzgi / День", callback_data="day_shift"
                        ),
                        InlineKeyboardButton(
                            text="🌙 Tungi / Ночь", callback_data="night_shift"
                        ),
                    ],
                    [InlineKeyboardButton(text="📃 Hisobot", callback_data="report")],
                ]
            )

        @staticmethod
        def admin_menu() -> InlineKeyboardMarkup:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💳 To'lov amalga oshirish", callback_data="pay"
                        )
                    ],
                    [InlineKeyboardButton(text="📃 Hisobot", callback_data="report")],
                ]
            )

    class Pickers:
        @staticmethod
        def time_picker_kb(
            hour: Optional[int] = 8,
            minutes: Optional[int] = 30,
            min_hour: Optional[int] = 7,
            min_minutes: Optional[int] = 0,
            max_hour: Optional[int] = 19,
            max_minutes: Optional[int] = 30,
        ) -> InlineKeyboardMarkup:
            now = f"{hour:02d}:{minutes:02d}"
            min_t = f"{min_hour:02d}:{min_minutes:02d}"
            max_t = f"{max_hour:02d}:{max_minutes:02d}"
            # Limits:
            if now == min_t:
                minus = max_t  # turn to maximum
                if min_minutes == 30:
                    plus = f"{(min_hour + 1):02d}:{0:02d}"
                else:
                    plus = f"{min_hour:02d}:{30:02d}"
            elif now == max_t:
                if max_minutes == 30:
                    minus = f"{(max_hour):02d}:{0:02d}"
                else:
                    minus = f"{(max_hour - 1):02d}:{30:02d}"
                plus = min_t  # turn to minimum
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
                        InlineKeyboardButton(
                            text="❌ Bekor qilish", callback_data="cancel"
                        ),
                        InlineKeyboardButton(
                            text="✅ Tayyor", callback_data=f"accept_{now}"
                        ),
                    ],
                ]
            )
            return kb

        @staticmethod
        def duration_picker_kb(
            hour: Optional[int] = 0, minutes: Optional[int] = 0
        ) -> InlineKeyboardMarkup:
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
                        InlineKeyboardButton(
                            text=duration, callback_data=f"pause_{duration}"
                        ),
                        InlineKeyboardButton(text="+", callback_data=plus),
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Bekor qilish", callback_data="cancel"
                        ),
                        InlineKeyboardButton(
                            text="✅ Tayyor", callback_data=f"accept_{duration}"
                        ),
                    ],
                ]
            )
            return kb

        @staticmethod
        def count_picker_kb(current: int) -> InlineKeyboardMarkup:
            minus = (current - 1) if current > 1 else 20
            plus = current + 1 if current < 20 else 1
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="-", callback_data=str(minus)),
                        InlineKeyboardButton(
                            text=f"{current}", callback_data=f"count_{current}"
                        ),
                        InlineKeyboardButton(text="+", callback_data=str(plus)),
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Bekor qilish", callback_data="cancel"
                        ),
                        InlineKeyboardButton(
                            text="✅ Tayyor", callback_data=f"accept_{current}"
                        ),
                    ],
                ]
            )

    class Shift:
        @staticmethod
        def roles_keyboard(used_roles: Optional[list] = []) -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            for role in RoleENUM:
                text = f"➕ {role.value.title()}"
                if role.value.upper() in used_roles:
                    text = text.replace("➕", "✅")
                kb.add(
                    InlineKeyboardButton(text=text, callback_data=f"role_{role.value.upper()}")
                )
            kb.add(
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"),
                InlineKeyboardButton(
                    text="✅ Tayyor. Adminga jo'natish",
                    callback_data="accept_shift_report",
                ),
            )
            return kb.adjust(2).as_markup()

        @staticmethod
        def approve_or_cancel_shift_kb(shift_id: int) -> InlineKeyboardMarkup:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Qabul qilish.", callback_data=f"approve_{shift_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Bekor qilish", callback_data=f"cancel_{shift_id}"
                        )
                    ],
                ]
            )
