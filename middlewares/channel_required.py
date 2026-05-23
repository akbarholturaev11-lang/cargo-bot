from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
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
            "confirmed": "✅ Обуна тасдиқ шуд.",
        },
        "ru": {
            "open": "📢 Перейти в канал",
            "check": "✅ Я подписался",
            "need": "📢 Сначала подпишитесь на канал.",
            "not_found": "❌ Подписка не найдена",
            "confirmed": "✅ Подписка подтверждена.",
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


async def _remove_subscribe_block(
    message: Message | None,
    *,
    fallback_text: str,
) -> None:
    if message is None:
        return

    try:
        await message.delete()
        return
    except (AttributeError, TelegramBadRequest, TelegramForbiddenError):
        pass

    # Agar delete bo‘lmasa, blokni obuna chaqirig'i holatida qoldirmaydi.
    try:
        await message.edit_text(fallback_text, reply_markup=None)
        return
    except (AttributeError, TelegramBadRequest, TelegramForbiddenError):
        pass

    try:
        await message.edit_reply_markup(reply_markup=None)
    except (AttributeError, TelegramBadRequest, TelegramForbiddenError):
        pass


class ChannelRequiredMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._subscribe_blocks: dict[tuple[int, int], int] = {}

    @staticmethod
    def _block_key(event: TelegramObject, user_id: int) -> tuple[int, int] | None:
        if isinstance(event, Message):
            return (event.chat.id, user_id)

        if isinstance(event, CallbackQuery) and event.message is not None:
            return (event.message.chat.id, user_id)

        return None

    async def _remove_saved_subscribe_block(
        self,
        bot,
        key: tuple[int, int] | None,
        *,
        current_message_id: int | None = None,
    ) -> None:
        if key is None:
            return

        message_id = self._subscribe_blocks.pop(key, None)
        if message_id is None or message_id == current_message_id:
            return

        chat_id, _ = key
        try:
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        except (TelegramBadRequest, TelegramForbiddenError):
            pass

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
        block_key = self._block_key(event, tg_user.id)

        if isinstance(event, CallbackQuery) and event.data == CHECK_SUB_CALLBACK:
            subscribed = await is_user_subscribed(bot, tg_user.id)

            if subscribed:
                self._subscribe_blocks.pop(block_key, None)
                await _remove_subscribe_block(
                    event.message,
                    fallback_text=_txt(lang, "confirmed"),
                )
                await event.answer(_txt(lang, "confirmed"))
                return

            await event.answer(_txt(lang, "not_found"), show_alert=True)
            return

        subscribed = await is_user_subscribed(bot, tg_user.id)
        if subscribed:
            await self._remove_saved_subscribe_block(bot, block_key)
            return await handler(event, data)

        if isinstance(event, Message):
            await self._remove_saved_subscribe_block(bot, block_key)
            block_message = await event.answer(
                _txt(lang, "need"),
                reply_markup=_subscribe_keyboard(channel, lang),
            )
            if block_key is not None:
                self._subscribe_blocks[block_key] = block_message.message_id
            return

        if isinstance(event, CallbackQuery):
            await event.answer()
            await self._remove_saved_subscribe_block(bot, block_key)
            if event.message is not None:
                block_message = await event.message.answer(
                    _txt(lang, "need"),
                    reply_markup=_subscribe_keyboard(channel, lang),
                )
                if block_key is not None:
                    self._subscribe_blocks[block_key] = block_message.message_id
            return

        return
