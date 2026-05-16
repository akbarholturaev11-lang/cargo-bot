from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from services.settings import get_setting
from services.settings import DEFAULT_SETTINGS


def normalize_channel_username(username: str | None) -> str | None:
    if not username:
        return None

    username = str(username).strip()
    if not username:
        return None

    if username.startswith("https://t.me/"):
        username = username.replace("https://t.me/", "@")

    if not username.startswith("@"):
        username = "@" + username

    return username


async def is_channel_join_required() -> bool:
    value = await get_setting(
        "require_channel_join",
        DEFAULT_SETTINGS.get("require_channel_join", False),
    )
    return str(value).lower() in {"true", "1", "yes", "on"}


async def get_required_channel() -> str | None:
    username = await get_setting(
        "channel_username",
        DEFAULT_SETTINGS.get("channel_username", ""),
    )
    return normalize_channel_username(username)


async def is_user_subscribed(bot: Bot, user_id: int) -> bool:
    required = await is_channel_join_required()
    if not required:
        return True

    channel = await get_required_channel()
    if not channel:
        return True

    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        return False

    return member.status in {
        "creator",
        "administrator",
        "member",
    }
