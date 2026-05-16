from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from handlers.user_menu import get_current_user
from keyboards.inline_user import warehouse_city_keyboard
from services.users import get_user_by_telegram_id
from services.warehouses import get_active_warehouse
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


@router.message(F.text.in_(WAREHOUSE_MENU_LABELS))
async def show_warehouse_cities(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    await message.answer(
        _texts(user.language).ASK_CITY,
        reply_markup=warehouse_city_keyboard(user.language),
    )


@router.callback_query(F.data == "warehouse:choose")
async def show_warehouse_cities_from_callback(callback: CallbackQuery) -> None:
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

    caption = texts.WAREHOUSE_ACTIVE.format(
        city=_city_name(city_key, lang),
        caption=warehouse.address_caption,
    )
    if callback.message is not None:
        await callback.message.answer_photo(
            photo=warehouse.image_file_id,
            caption=caption,
        )
    await callback.answer()
