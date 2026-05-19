import logging
from datetime import date, datetime

from aiogram import F, Router
from aiogram.types import Message

from handlers.user_menu import get_current_user
from services.parcels import get_parcels_by_client_code
from texts import ru, tj
from texts.status import format_status
from utils.constants import LANG_RU, LANG_TJ


logger = logging.getLogger(__name__)

router = Router(name="my_parcels")


MY_PARCELS_MENU_LABELS = {tj.MENU_MY_PARCELS, ru.MENU_MY_PARCELS}
MY_PARCELS_MENU_LABELS.update({"Борҳои ман", "Мои грузы"})
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
    try:
        user = await get_current_user(message)
        if user is None:
            await message.answer(tj.CHOOSE_LANGUAGE)
            return

        texts = _texts(user.language)

        logger.warning(
            "[MY_PARCELS] user_id=%s telegram_id=%s phone=%s client_code=%s",
            getattr(user, "id", None),
            getattr(user, "telegram_id", None),
            getattr(user, "phone", None),
            getattr(user, "client_code", None),
        )

        parcels = await get_parcels_by_client_code(user.client_code)
        logger.warning("[MY_PARCELS] parcels_count=%s", len(parcels))

        if not parcels:
            await message.answer(texts.MY_PARCELS_EMPTY)
            return

        parcel_blocks = []

        for index, parcel in enumerate(parcels, start=1):
            logger.warning(
                "[MY_PARCELS] parcel id=%s track=%s status=%s city=%s received=%s",
                getattr(parcel, "id", None),
                getattr(parcel, "track_code", None),
                getattr(parcel, "status_code", None),
                getattr(parcel, "destination_city", None),
                getattr(parcel, "received_china_at", None),
            )

            try:
                block = texts.MY_PARCELS_ITEM.format(
                    index=index,
                    track_code=getattr(parcel, "track_code", "") or "—",
                    dynamic_status=format_status(
                        getattr(parcel, "status_code", None),
                        getattr(parcel, "destination_city", None),
                        user.language,
                    ),
                    destination_city=getattr(parcel, "destination_city", None) or "—",
                    received_china_at=_format_date(
                        getattr(parcel, "received_china_at", None)
                    ),
                )
            except Exception:
                logger.exception("[MY_PARCELS] failed to format parcel item")
                block = (
                    "📦 <b>{index}. Бор</b>\n"
                    "🔢 Трек-код: <code>{track}</code>\n"
                    "📍 Статус: <b>{status}</b>"
                ).format(
                    index=index,
                    track=getattr(parcel, "track_code", "") or "—",
                    status=getattr(parcel, "status_code", "") or "—",
                )

            parcel_blocks.append(block)

        await message.answer(
            f"{texts.MY_PARCELS_TITLE}\n\n" + "\n\n".join(parcel_blocks)
        )

    except Exception:
        logger.exception("[MY_PARCELS_ERROR] failed")

        user = await get_current_user(message)
        lang = getattr(user, "language", "tj") if user else "tj"

        if lang == "ru":
            text = (
                "❌ <b>Ошибка при загрузке ваших грузов.</b>\n\n"
                "<blockquote>Попробуйте позже или напишите оператору.</blockquote>"
            )
        else:
            text = (
                "❌ <b>Ҳангоми нишон додани борҳои шумо хатогӣ шуд.</b>\n\n"
                "<blockquote>Лутфан баъдтар такрор кунед ё ба оператор нависед.</blockquote>"
            )

        await message.answer(text)
