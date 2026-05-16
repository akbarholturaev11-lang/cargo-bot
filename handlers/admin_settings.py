from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline_admin import (
    settings_calculation_keyboard,
    settings_categories_keyboard,
    settings_channel_keyboard,
    settings_delivery_keyboard,
    settings_operator_keyboard,
    settings_prices_keyboard,
    settings_texts_keyboard,
)
from keyboards.reply import ADMIN_MENU, admin_main_menu
from services.settings import (
    DEFAULT_SETTINGS,
    get_many_settings,
    get_setting,
    set_setting,
    toggle_bool_setting,
)
from states.admin_settings_states import AdminSettingsStates
from utils.validators import is_admin


router = Router(name="admin_settings")


ADMIN_SETTINGS_LABEL = ADMIN_MENU[4][0]
EDITABLE_SETTINGS = {
    "price_per_kg_tjs",
    "price_per_cube_tjs",
    "delivery_days_tj",
    "delivery_days_ru",
    "delivery_inside_city_tj",
    "delivery_outside_city_tj",
    "delivery_inside_city_ru",
    "delivery_outside_city_ru",
    "channel_username",
    "operator_username",
    "operator_phone",
    "operator_whatsapp",
}
TOGGLE_SETTINGS = {
    "delivery_enabled": False,
    "require_channel_join": False,
}


def _is_admin_message(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _is_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)


def _display_value(value: str | None) -> str:
    return value if value else "-"


async def _prices_text(title: str = "Нархҳо") -> str:
    values = await get_many_settings(
        {
            "price_per_kg_tjs": DEFAULT_SETTINGS["price_per_kg_tjs"],
            "price_per_cube_tjs": DEFAULT_SETTINGS["price_per_cube_tjs"],
            "delivery_days_tj": DEFAULT_SETTINGS["delivery_days_tj"],
            "delivery_days_ru": DEFAULT_SETTINGS["delivery_days_ru"],
        },
    )
    return (
        f"{title}\n\n"
        f"price_per_kg_tjs: {values['price_per_kg_tjs']}\n"
        f"price_per_cube_tjs: {values['price_per_cube_tjs']}\n"
        f"delivery_days_tj: {values['delivery_days_tj']}\n"
        f"delivery_days_ru: {values['delivery_days_ru']}"
    )


async def _calculation_text() -> str:
    values = await get_many_settings(
        {
            "price_per_kg_tjs": DEFAULT_SETTINGS["price_per_kg_tjs"],
            "price_per_cube_tjs": DEFAULT_SETTINGS["price_per_cube_tjs"],
        },
    )
    return (
        "Ҳисобкунӣ\n\n"
        f"price_per_kg_tjs: {values['price_per_kg_tjs']}\n"
        f"price_per_cube_tjs: {values['price_per_cube_tjs']}"
    )


async def _delivery_text() -> str:
    values = await get_many_settings(
        {
            "delivery_enabled": DEFAULT_SETTINGS["delivery_enabled"],
            "delivery_inside_city_tj": DEFAULT_SETTINGS["delivery_inside_city_tj"],
            "delivery_outside_city_tj": DEFAULT_SETTINGS["delivery_outside_city_tj"],
            "delivery_inside_city_ru": DEFAULT_SETTINGS["delivery_inside_city_ru"],
            "delivery_outside_city_ru": DEFAULT_SETTINGS["delivery_outside_city_ru"],
        },
    )
    return (
        "Доставка\n\n"
        f"delivery_enabled: {values['delivery_enabled']}\n"
        f"delivery_inside_city_tj: {values['delivery_inside_city_tj']}\n"
        f"delivery_outside_city_tj: {values['delivery_outside_city_tj']}\n"
        f"delivery_inside_city_ru: {values['delivery_inside_city_ru']}\n"
        f"delivery_outside_city_ru: {values['delivery_outside_city_ru']}"
    )


async def _channel_text() -> str:
    values = await get_many_settings(
        {
            "require_channel_join": DEFAULT_SETTINGS["require_channel_join"],
            "channel_username": DEFAULT_SETTINGS["channel_username"],
        },
    )
    return (
        "Канал\n\n"
        f"require_channel_join: {values['require_channel_join']}\n"
        f"channel_username: {_display_value(values['channel_username'])}"
    )


async def _operator_text() -> str:
    values = await get_many_settings(
        {
            "operator_username": DEFAULT_SETTINGS["operator_username"],
            "operator_phone": DEFAULT_SETTINGS["operator_phone"],
            "operator_whatsapp": DEFAULT_SETTINGS["operator_whatsapp"],
        },
    )
    return (
        "Оператор\n\n"
        f"operator_username: {_display_value(values['operator_username'])}\n"
        f"operator_phone: {_display_value(values['operator_phone'])}\n"
        f"operator_whatsapp: {_display_value(values['operator_whatsapp'])}"
    )


async def _texts_text() -> str:
    values = await get_many_settings(
        {
            "delivery_days_tj": DEFAULT_SETTINGS["delivery_days_tj"],
            "delivery_days_ru": DEFAULT_SETTINGS["delivery_days_ru"],
            "delivery_inside_city_tj": DEFAULT_SETTINGS["delivery_inside_city_tj"],
            "delivery_outside_city_tj": DEFAULT_SETTINGS["delivery_outside_city_tj"],
            "delivery_inside_city_ru": DEFAULT_SETTINGS["delivery_inside_city_ru"],
            "delivery_outside_city_ru": DEFAULT_SETTINGS["delivery_outside_city_ru"],
        },
    )
    return (
        "Матнҳо\n\n"
        f"delivery_days_tj: {values['delivery_days_tj']}\n"
        f"delivery_days_ru: {values['delivery_days_ru']}\n"
        f"delivery_inside_city_tj: {values['delivery_inside_city_tj']}\n"
        f"delivery_outside_city_tj: {values['delivery_outside_city_tj']}\n"
        f"delivery_inside_city_ru: {values['delivery_inside_city_ru']}\n"
        f"delivery_outside_city_ru: {values['delivery_outside_city_ru']}"
    )


async def _screen(category: str):
    if category == "prices":
        return await _prices_text(), settings_prices_keyboard()
    if category == "calculation":
        return await _calculation_text(), settings_calculation_keyboard()
    if category == "delivery":
        return await _delivery_text(), settings_delivery_keyboard()
    if category == "channel":
        return await _channel_text(), settings_channel_keyboard()
    if category == "operator":
        return await _operator_text(), settings_operator_keyboard()
    if category == "texts":
        return await _texts_text(), settings_texts_keyboard()
    return "Танзимот", settings_categories_keyboard()


async def _edit_category_message(message: Message, category: str) -> None:
    text, keyboard = await _screen(category)
    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            reply_markup=keyboard,
        )
    except TelegramBadRequest:
        await message.answer(text, reply_markup=keyboard)


@router.message(F.text == ADMIN_SETTINGS_LABEL)
async def show_admin_settings(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.clear()
    await message.answer("Танзимот", reply_markup=settings_categories_keyboard())


@router.callback_query(F.data == "settings:main")
async def show_settings_main(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    if callback.message is not None:
        await callback.message.edit_text(
            "Танзимот",
            reply_markup=settings_categories_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    F.data.in_(
        {
            "settings:prices",
            "settings:calculation",
            "settings:delivery",
            "settings:channel",
            "settings:operator",
            "settings:texts",
        },
    ),
)
async def show_settings_category(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    category = callback.data.split(":", 1)[1]
    if callback.message is not None:
        text, keyboard = await _screen(category)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "settings:back")
async def settings_back(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    if callback.message is not None:
        await callback.message.edit_text("Панели админ")
        await callback.message.answer("Панели админ", reply_markup=admin_main_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("settings:toggle:"))
async def toggle_setting(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    key = callback.data.rsplit(":", 1)[1]
    if key not in TOGGLE_SETTINGS:
        await callback.answer()
        return

    await toggle_bool_setting(key, TOGGLE_SETTINGS[key])
    category = "delivery" if key == "delivery_enabled" else "channel"
    if callback.message is not None:
        text, keyboard = await _screen(category)
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer("Нав шуд")


@router.callback_query(F.data.startswith("settings:edit:"))
async def start_edit_setting(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    key = callback.data.rsplit(":", 1)[1]
    if key not in EDITABLE_SETTINGS:
        await callback.answer()
        return

    current_value = await get_setting(key, DEFAULT_SETTINGS.get(key, ""))
    category = _category_for_key(key)
    await state.set_state(AdminSettingsStates.waiting_for_value)
    if callback.message is not None:
        await state.update_data(
            key=key,
            category=category,
            settings_message_id=callback.message.message_id,
        )
        await callback.message.edit_text(
            f"{key}\n\n"
            f"Ҳозира: {_display_value(current_value)}\n\n"
            "Қимати навро фиристед. Барои холӣ кардан '-' фиристед.",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("settings:edit_text:"))
async def start_edit_text_setting(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    key = callback.data.rsplit(":", 1)[1]
    if key not in EDITABLE_SETTINGS:
        await callback.answer()
        return

    current_value = await get_setting(key, DEFAULT_SETTINGS.get(key, ""))
    await state.set_state(AdminSettingsStates.waiting_for_value)
    if callback.message is not None:
        await state.update_data(
            key=key,
            category="texts",
            settings_message_id=callback.message.message_id,
        )
        await callback.message.edit_text(
            f"{key}\n\n"
            f"Ҳозира: {_display_value(current_value)}\n\n"
            "Қимати навро фиристед. Барои холӣ кардан '-' фиристед.",
        )
    await callback.answer()


@router.message(AdminSettingsStates.waiting_for_value, F.text)
async def save_setting_value(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    data = await state.get_data()
    key = data["key"]
    value = "" if message.text.strip() == "-" else message.text.strip()
    await set_setting(key, value)

    category = data.get("category", "main")
    message_id = data.get("settings_message_id")
    await state.clear()

    text, keyboard = await _screen(category)
    if message_id is None:
        await message.answer(text, reply_markup=keyboard)
        return

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
        )
    except TelegramBadRequest:
        await message.answer(text, reply_markup=keyboard)


def _category_for_key(key: str) -> str:
    price_keys = {
        "price_per_kg_tjs",
        "price_per_cube_tjs",
        "delivery_days_tj",
        "delivery_days_ru",
    }
    if key in price_keys:
        return "prices"
    if key.startswith("delivery_"):
        return "delivery"
    if key in {"channel_username"}:
        return "channel"
    if key.startswith("operator_"):
        return "operator"
    return "main"
