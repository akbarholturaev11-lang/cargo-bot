from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, TelegramObject
from aiogram.exceptions import TelegramBadRequest

from config import ADMIN_IDS
from services.channel import get_required_channel, is_channel_join_required, is_user_subscribed

CHECK_SUB_CALLBACK = "channel:check"


def _channel_url(channel: str) -> str:
    channel = (channel or "").strip()

    if channel.startswith("https://t.me/"):
        return channel

    if channel.startswith("@"):
        return f"https://t.me/{channel[1:]}"

    return f"https://t.me/{channel}"


def _subscribe_keyboard(channel: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Каналга ўтиш",
                    url=_channel_url(channel),
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Обуна бўлдим",
                    callback_data=CHECK_SUB_CALLBACK,
                )
            ],
        ]
    )


async def _safe_delete_message(message) -> None:
    if not message:
        return

    try:
        await message.delete()
    except TelegramBadRequest:
        return


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

        # User "✅ Обуна бўлдим" босганда middleware ўзи текширади
        if isinstance(event, CallbackQuery) and event.data == CHECK_SUB_CALLBACK:
            subscribed = await is_user_subscribed(bot, tg_user.id)

            if subscribed:
                await event.answer("✅ Обуна тасдиқ шуд")
                await _safe_delete_message(event.message)

                await event.message.answer(
                    "✅ Обуна тасдиқ шуд. Акнун ботдан фойдаланишингиз мумкин.\n\n"
                    "Бошлаш учун /start босинг."
                )
                return

            await event.answer("❌ Ҳали обуна бўлмагансиз", show_alert=True)
            return

        subscribed = await is_user_subscribed(bot, tg_user.id)
        if subscribed:
            return await handler(event, data)

        text = (
            "📢 <b>Ботдан фойдаланиш учун аввал каналга обуна бўлинг.</b>\n\n"
            "Обуна бўлгандан кейин <b>✅ Обуна бўлдим</b> тугмасини босинг."
        )

        if isinstance(event, Message):
            await event.answer(text, reply_markup=_subscribe_keyboard(channel))
            return

        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.answer(text, reply_markup=_subscribe_keyboard(channel))
            return

        return
