from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, TelegramObject

from config import ADMIN_IDS
from keyboards.reply import user_main_menu
from services.channel import get_required_channel, is_channel_join_required, is_user_subscribed
from services.users import get_or_create_user


CHECK_SUB_CALLBACK = "channel:check"


def _channel_url(channel: str) -> str:
    channel = (channel or "").strip()
    if channel.startswith("@"):
        return f"https://t.me/{channel[1:]}"
    if channel.startswith("https://t.me/"):
        return channel
    return f"https://t.me/{channel}"


def _subscribe_keyboard(channel: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Ба канал обуна шавед",
                    url=_channel_url(channel),
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Обуна шудам",
                    callback_data=CHECK_SUB_CALLBACK,
                )
            ],
        ]
    )


class ChannelRequiredMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        bot = data.get("bot")
        user = data.get("event_from_user")

        if user is None or bot is None:
            return await handler(event, data)

        if user.id in ADMIN_IDS:
            return await handler(event, data)

        required = await is_channel_join_required()
        if not required:
            return await handler(event, data)

        channel = await get_required_channel()
        if not channel:
            return await handler(event, data)

        # "Обуна шудам" callback'ини middleware ўзи текширади
        if isinstance(event, CallbackQuery) and event.data == CHECK_SUB_CALLBACK:
            subscribed = await is_user_subscribed(bot, user.id)

            if subscribed:
                db_user = await get_or_create_user(user)
                lang = getattr(db_user, "language", "tj") or "tj"

                await event.answer("✅ Обуна тасдиқ шуд")
                await event.message.answer(
                    "✅ Обуна тасдиқ шуд. Акнун ботро истифода бурда метавонед.",
                    reply_markup=user_main_menu(lang),
                )
                return

            await event.answer("❌ Ҳанӯз обуна нашудаед", show_alert=True)
            await event.message.answer(
                f"📢 <b>Барои истифодаи бот аввал ба канал обуна шавед:</b>\n{channel}",
                reply_markup=_subscribe_keyboard(channel),
            )
            return

        subscribed = await is_user_subscribed(bot, user.id)
        if subscribed:
            return await handler(event, data)

        text = f"📢 <b>Барои истифодаи бот аввал ба канал обуна шавед:</b>\n{channel}"

        if isinstance(event, Message):
            await event.answer(text, reply_markup=_subscribe_keyboard(channel))
            return

        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.answer(text, reply_markup=_subscribe_keyboard(channel))
            return

        return
