from datetime import date, datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from database.models import Parcel, User
from keyboards.inline_user import delivery_keyboard
from services.settings import get_setting
from texts.status import format_status
from utils.constants import LANG_TJ, STATUS_CHINA_RECEIVED


def _format_date(value: datetime | date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y")


async def format_china_received_notification(parcel: Parcel) -> str:
    delivery_days = await get_setting("delivery_days_tj", "18–25 рӯз")
    return (
        "Бори шумо қабул шуд\n\n"
        f"Трек-код: {parcel.track_code}\n"
        f"Статус: {format_status(STATUS_CHINA_RECEIVED, parcel.destination_city, LANG_TJ)}\n"
        f"Склад: {parcel.destination_city}\n"
        f"Санаи қабул дар склади Чин: {_format_date(parcel.received_china_at)}\n"
        f"Муддати тахминии расидан: {delivery_days}\n\n"
        "Вазн ва маблағ баъди расидан маълум мешавад."
    )


async def notify_china_received(bot: Bot, user: User, parcel: Parcel) -> bool:
    if user.telegram_id is None or parcel.china_received_notified_at is not None:
        return False

    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=await format_china_received_notification(parcel),
        )
    except TelegramAPIError:
        return False

    return True


def format_arrival_notification(parcel: Parcel) -> str:
    return (
        f"Бори шумо ба склади {parcel.destination_city} расид\n\n"
        f"Трек-код: {parcel.track_code}\n"
        "Статус: Омода барои гирифтан\n\n"
        "Шумо метавонед борро аз склад гирифта баред ё хизматрасонии доставка интихоб кунед."
    )


async def notify_arrival_destination(bot: Bot, user: User, parcel: Parcel) -> bool:
    if user.telegram_id is None or parcel.arrival_notified_at is not None:
        return False

    try:
        await bot.send_message(
            chat_id=user.telegram_id,
            text=format_arrival_notification(parcel),
            reply_markup=delivery_keyboard(LANG_TJ),
        )
    except TelegramAPIError:
        return False

    return True
