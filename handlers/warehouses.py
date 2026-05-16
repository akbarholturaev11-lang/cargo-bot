from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from handlers.user_menu import get_current_user
from keyboards.inline_user import warehouse_city_keyboard
from services.delivery import get_arrived_parcel_for_user_by_id
from services.users import get_user_by_telegram_id
from services.warehouses import get_active_warehouse, get_user_warehouse, get_warehouse_for_parcel_destination
from texts import ru, tj
from utils.constants import CITY_NAMES, LANG_RU, LANG_TJ


router = Router(name="warehouses")


WAREHOUSE_MENU_LABELS = {tj.MENU_WAREHOUSES, ru.MENU_WAREHOUSES}
TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


def _city_name(city_key: str, lang: str) -> str:
    names = CITY_NAMES.get(city_key)
    if names is None:
        return city_key
    return names.get(lang, names[LANG_TJ])


def _warehouse_media(warehouse) -> tuple[str, str | None]:
    media_type = getattr(warehouse, "media_type", None) or "photo"
    media_file_id = getattr(warehouse, "media_file_id", None) or warehouse.image_file_id
    if media_type not in {"photo", "video", "text"}:
        media_type = "photo" if media_file_id else "text"
    if media_type in {"photo", "video"} and not media_file_id:
        media_type = "text"
    return media_type, media_file_id


async def _send_warehouse_block(
    target,
    warehouse,
    *,
    city: str,
    lang: str,
) -> None:
    message = target.message if isinstance(target, CallbackQuery) else target
    if message is None:
        return

    caption = _texts(lang).WAREHOUSE_ACTIVE.format(
        city=city,
        caption=warehouse.address_caption,
    )
    media_type, media_file_id = _warehouse_media(warehouse)
    if media_type == "photo" and media_file_id:
        await message.answer_photo(
            photo=media_file_id,
            caption=caption,
        )
    elif media_type == "video" and media_file_id:
        await message.answer_video(
            video=media_file_id,
            caption=caption,
        )
    else:
        await message.answer(caption)


@router.message(F.text.in_(WAREHOUSE_MENU_LABELS))
async def show_warehouse_cities(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    lang = user.language
    texts = _texts(lang)

    warehouse, mode = await get_user_warehouse(user.city)

    if mode == "no_warehouses" or warehouse is None and mode != "need_choose":
        await message.answer(
            "❌ <b>Айнихол ягон склад фаъол нест.</b>"
            if lang == LANG_TJ
            else "❌ <b>Сейчас нет активного склада.</b>"
        )
        return

    if warehouse is not None and mode in {"single", "user_city"}:
        city = warehouse.city_name_tj if lang == LANG_TJ else warehouse.city_name_ru
        await _send_warehouse_block(
            message,
            warehouse,
            city=city,
            lang=lang,
        )
        return

    await message.answer(
        texts.ASK_CITY,
        reply_markup=warehouse_city_keyboard(lang),
    )


@router.callback_query(F.data == "warehouse:choose")
async def show_warehouse_cities_from_callback(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("warehouse:arrival:"))
async def show_arrival_warehouse(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    lang = user.language if user is not None else LANG_TJ

    try:
        parcel_id = int(callback.data.rsplit(":", 1)[1])
    except (ValueError, AttributeError):
        await callback.answer()
        return

    parcel = None
    if user is not None:
        parcel = await get_arrived_parcel_for_user_by_id(
            user_id=user.id,
            parcel_id=parcel_id,
        )

    warehouse = None
    if parcel is not None:
        warehouse = await get_warehouse_for_parcel_destination(
            destination_warehouse_id=parcel.destination_warehouse_id,
            destination_city=parcel.destination_city,
        )

    if parcel is None or warehouse is None:
        if callback.message is not None:
            await callback.message.answer(_texts(lang).WAREHOUSE_ADDRESS_MISSING)
        await callback.answer()
        return

    await _send_warehouse_block(
        callback,
        warehouse,
        city=parcel.destination_city,
        lang=lang,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("warehouse:city:"))
async def show_warehouse(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    lang = user.language if user is not None else LANG_TJ
    texts = _texts(lang)
    city_key = callback.data.rsplit(":", 1)[1]
    if city_key not in CITY_NAMES:
        await callback.answer()
        return

    warehouse = await get_active_warehouse(city_key)
    if warehouse is None:
        if callback.message is not None:
            await callback.message.edit_text(
                texts.WAREHOUSE_INACTIVE,
                reply_markup=warehouse_city_keyboard(lang),
            )
        await callback.answer()
        return

    await _send_warehouse_block(
        callback,
        warehouse,
        city=_city_name(city_key, lang),
        lang=lang,
    )
    await callback.answer()
