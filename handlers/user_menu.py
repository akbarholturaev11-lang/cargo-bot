from aiogram import Router
from aiogram.types import Message

from services.users import get_user_by_telegram_id
from texts import ru, tj


router = Router(name="user_menu")


USER_MAIN_MENU_LABELS = {
    tj.MENU_SEARCH_PARCEL,
    tj.MENU_MY_PARCELS,
    tj.MENU_CALCULATOR,
    tj.MENU_PROFILE,
    tj.MENU_WAREHOUSES,
    tj.MENU_PRICES,
    tj.MENU_OPERATOR,
    ru.MENU_SEARCH_PARCEL,
    ru.MENU_MY_PARCELS,
    ru.MENU_CALCULATOR,
    ru.MENU_PROFILE,
    ru.MENU_WAREHOUSES,
    ru.MENU_PRICES,
    ru.MENU_OPERATOR,
}

PROFILE_MENU_LABELS = {tj.MENU_PROFILE, ru.MENU_PROFILE}


async def get_current_user(message: Message):
    if message.from_user is None:
        return None
    return await get_user_by_telegram_id(message.from_user.id)
