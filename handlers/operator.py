from aiogram import F, Router
from aiogram.types import Message

from handlers.user_menu import get_current_user
from services.settings import DEFAULT_SETTINGS, get_many_settings
from texts import ru, tj
from utils.constants import LANG_RU, LANG_TJ

router = Router(name="operator")


TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}

OPERATOR_MENU_LABELS = {tj.MENU_OPERATOR, ru.MENU_OPERATOR}
PRICES_MENU_LABELS = {tj.MENU_PRICES, ru.MENU_PRICES}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


async def _delivery_days(lang: str) -> str:
    key = "delivery_days_ru" if lang == LANG_RU else "delivery_days_tj"
    default = DEFAULT_SETTINGS[key]
    values = await get_many_settings({key: default})
    return values[key]


@router.message(F.text.in_(OPERATOR_MENU_LABELS))
async def show_operator(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    values = await get_many_settings(
        {
            "operator_username": DEFAULT_SETTINGS["operator_username"],
            "operator_phone": DEFAULT_SETTINGS["operator_phone"],
            "operator_whatsapp": DEFAULT_SETTINGS["operator_whatsapp"],
        },
    )
    contacts = [
        value
        for value in (
            values["operator_username"],
            values["operator_phone"],
            values["operator_whatsapp"],
        )
        if value
    ]
    if not contacts:
        await message.answer(texts.OPERATOR_NOT_SET)
        return

    await message.answer(texts.OPERATOR.format(contacts="\n".join(contacts)))


@router.message(F.text.in_(PRICES_MENU_LABELS))
async def show_prices(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    values = await get_many_settings(
        {
            "price_per_kg_tjs": DEFAULT_SETTINGS["price_per_kg_tjs"],
            "price_per_cube_tjs": DEFAULT_SETTINGS["price_per_cube_tjs"],
        },
    )
    await message.answer(
        texts.PRICES.format(
            price_per_kg_tjs=values["price_per_kg_tjs"],
            price_per_cube_tjs=values["price_per_cube_tjs"],
            delivery_days=await _delivery_days(user.language),
        ),
    )
