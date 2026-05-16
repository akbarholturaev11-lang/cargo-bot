from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from config import ADMIN_IDS
from services.channel import get_required_channel, is_channel_join_required, is_user_subscribed


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

        subscribed = await is_user_subscribed(bot, user.id)
        if subscribed:
            return await handler(event, data)

        text = f"📢 <b>Барои истифодаи бот ба канал обуна шавед:</b> {channel}"

        if isinstance(event, Message):
            await event.answer(text)
            return

        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.answer(text)
            return

        return
