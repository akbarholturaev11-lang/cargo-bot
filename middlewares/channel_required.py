from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    TelegramObject,
)

from config import ADMIN_IDS
from services.channel import get_required_channel, is_channel_join_required, is_user_subscribed

CHECK_SUB_CALLBACK = "channel:check"


def _lang(tg_user) -> str:
    code = (getattr(tg_user, "language_code", "") or "").lower()
    if code.startswith("ru"):
        return "ru"
    return "tj"


def _txt(lang: str, key: str) -> str:
    texts = {
        "tj": {
            "open": "📢 Ба канал обуна шавед",
            "check": "✅ Обуна шудам",
            "need": "📢 Аввал ба канал обуна шавед.",
            "not_found": "❌ Обуна ёфт нашуд",
        },
        "ru": {
            "open": "📢 Перейти в канал",
            "check": "✅ Я подписался",
            "need": "📢 Сначала подпишитесь на канал.",
            "not_found": "❌ Подписка не найдена",
        },
    }
    return texts.get(lang, texts["tj"])[key]


def _channel_url(channel: str) -> str:
    channel = (channel or "").strip()

    if channel.startswith("https://t.me/"):
        return channel

    if channel.startswith("@"):
        return f"https://t.me/{channel[1:]}"

    return f"https://t.me/{channel}"


def _subscribe_keyboard(channel: str, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_txt(lang, "open"),
                    url=_channel_url(channel),
                )
            ],
            [
                InlineKeyboardButton(
                    text=_txt(lang, "check"),
                    callback_data=CHECK_SUB_CALLBACK,
                )
            ],
        ]
    )


async def _remove_subscribe_block(message: Message) -> None:
    try:
        await message.delete()
        return
    except TelegramBadRequest:
        pass

    # Agar delete bo‘lmasa, hech bo‘lmasa knopkalarni olib tashlaydi
    try:
        await message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass


class ChannelRequiredMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot = data.get("bot")
        tg_user = data.get("event_from_user")

        if tg_user is None or bot is None:
            return await handler(event, data)

        if tg_user.id in ADMIN_IDS:
            return await handler(event, data)

        required = await is_channel_join_required()
        if not required:
            return await handler(event, data)

        channel = await get_required_channel()
        if not channel:
            return await handler(event, data)

        lang = _lang(tg_user)

        if isinstance(event, CallbackQuery) and event.data == CHECK_SUB_CALLBACK:
            subscribed = await is_user_subscribed(bot, tg_user.id)

            if subscribed:
                await event.answer()
                await _remove_subscribe_block(event.message)
                return

            await event.answer(_txt(lang, "not_found"), show_alert=True)
            return

        subscribed = await is_user_subscribed(bot, tg_user.id)
        if subscribed:
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer(
                _txt(lang, "need"),
                reply_markup=_subscribe_keyboard(channel, lang),
            )
            return

        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.answer(
                _txt(lang, "need"),
                reply_markup=_subscribe_keyboard(channel, lang),
            )
            return

        return
