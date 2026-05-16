from datetime import date, datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from database.models import Parcel, User
from keyboards.inline_user import delivery_keyboard
from services.settings import get_setting
from texts import ru, tj
from texts.status import format_status
from utils.constants import LANG_RU, LANG_TJ, STATUS_CHINA_RECEIVED


def _format_date(value: datetime | date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y")


def _texts(lang: str):
    return ru if lang == LANG_RU else tj


async def format_china_received_notification(parcel: Parcel, lang: str = LANG_TJ) -> str:
    texts = _texts(lang)
    delivery_days_key = "delivery_days_ru" if lang == LANG_RU else "delivery_days_tj"
    delivery_days_default = "18–25 дней" if lang == LANG_RU else "18–25 рӯз"
    delivery_days = await get_setting(delivery_days_key, delivery_days_default)
    return texts.NOTIFICATION_CHINA_RECEIVED.format(
        track_code=parcel.track_code,
        status=format_status(STATUS_CHINA_RECEIVED, parcel.destination_city, lang),
        destination_city=parcel.destination_city,
        received_china_at=_format_date(parcel.received_china_at),
        delivery_days=delivery_days,
    )


async def notify_china_received(bot: Bot, user: User, parcel: Parcel) -> bool:
    if user.telegram_id is None or parcel.china_received_notified_at is not None:
        return False

    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=await format_china_received_notification(parcel, user.language),
        )
    except TelegramAPIError:
        return False

    return True


def format_arrival_notification(parcel: Parcel, lang: str = LANG_TJ) -> str:
    return _texts(lang).NOTIFICATION_ARRIVED.format(
        city=parcel.destination_city,
        track_code=parcel.track_code,
    )


async def notify_arrival_destination(bot: Bot, user: User, parcel: Parcel) -> bool:
    if user.telegram_id is None or parcel.arrival_notified_at is not None:
        return False

    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=format_arrival_notification(parcel, user.language),
            reply_markup=delivery_keyboard(user.language, parcel.id),
        )
    except TelegramAPIError:
        return False

    return True
