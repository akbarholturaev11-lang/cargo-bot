from datetime import date, datetime

from aiogram import F, Router
from aiogram.types import Message

from handlers.user_menu import get_current_user
from services.parcels import get_parcels_by_client_code
from texts import ru, tj
from texts.status import format_status
from utils.constants import LANG_RU, LANG_TJ


router = Router(name="my_parcels")


MY_PARCELS_MENU_LABELS = {tj.MENU_MY_PARCELS, ru.MENU_MY_PARCELS}
TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


def _format_date(value: datetime | date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y")


def _format_parcel_item(parcel, lang: str) -> str:
    texts = _texts(lang)
    return texts.MY_PARCELS_ITEM.format(
        track_code=parcel.track_code,
        dynamic_status=format_status(
            parcel.status_code,
            parcel.destination_city,
            lang,
        ),
        destination_city=parcel.destination_city,
        received_china_at=_format_date(parcel.received_china_at),
    )


@router.message(F.text.in_(MY_PARCELS_MENU_LABELS))
async def show_my_parcels(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    parcels = await get_parcels_by_client_code(user.client_code)
    if not parcels:
        await message.answer(texts.MY_PARCELS_EMPTY)
        return

    parcel_blocks = [
        _format_parcel_item(parcel, user.language)
        for parcel in parcels
    ]
    await message.answer(f"{texts.MY_PARCELS_TITLE}\n\n" + "\n\n".join(parcel_blocks))
