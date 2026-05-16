from collections.abc import Sequence

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def build_reply_keyboard(
    rows: Sequence[Sequence[str]],
    *,
    resize_keyboard: bool = True,
    one_time_keyboard: bool = False,
) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=label) for label in row]
        for row in rows
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard,
    )


def build_contact_keyboard(label: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def build_inline_keyboard(
    rows: Sequence[Sequence[tuple[str, str]]],
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text=label, callback_data=callback_data)
            for label, callback_data in row
        ]
        for row in rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
