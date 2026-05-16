from aiogram.types import InlineKeyboardMarkup

from keyboards.builders import build_inline_keyboard
from utils.constants import (
    CITY_BOKHTAR,
    CITY_DUSHANBE,
    CITY_ISTARAVSHAN,
    CITY_KHUJAND,
    CITY_KULOB,
    CITY_NAMES,
    LANG_TJ,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
)


def admin_confirm_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Тасдиқ", "admin:confirm"), ("Бекор", "admin:cancel")),
        ),
    )


def parcel_statuses_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Дар склади Чин", f"parcel_status:{STATUS_CHINA_RECEIVED}"),),
            (("Дар роҳ", f"parcel_status:{STATUS_ON_THE_WAY}"),),
            (("Ба склад расид", f"parcel_status:{STATUS_ARRIVED_DESTINATION}"),),
        ),
    )


def settings_categories_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Нархҳо", "settings:prices"),),
            (("Ҳисобкунӣ", "settings:calculation"),),
            (("Доставка", "settings:delivery"),),
            (("Складҳо", "settings:warehouses"),),
            (("Канал", "settings:channel"),),
            (("Оператор", "settings:operator"),),
            (("Матнҳо", "settings:texts"),),
            (("Бозгашт", "settings:back"),),
        ),
    )


def settings_prices_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("📦 Нархи 1 кг", "settings:edit:price_per_kg_tjs"),),
            (("📐 Нархи 1 куб", "settings:edit:price_per_cube_tjs"),),
            (("🚚 Муддати расидан TJ", "settings:edit:delivery_days_tj"),),
            (("🚚 Муддати расидан RU", "settings:edit:delivery_days_ru"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_calculation_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("📦 Нархи 1 кг", "settings:edit:price_per_kg_tjs"),),
            (("📐 Нархи 1 куб", "settings:edit:price_per_cube_tjs"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_delivery_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("🚚 Доставка ON/OFF", "settings:toggle:delivery_enabled"),),
            (("🏙 Дохили шаҳр TJ", "settings:edit:delivery_inside_city_tj"),),
            (("🚕 Берун аз шаҳр TJ", "settings:edit:delivery_outside_city_tj"),),
            (("🏙 Дохили шаҳр RU", "settings:edit:delivery_inside_city_ru"),),
            (("🚕 Берун аз шаҳр RU", "settings:edit:delivery_outside_city_ru"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_channel_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("📢 Обуна ба канал ON/OFF", "settings:toggle:require_channel_join"),),
            (("🔗 Username-и канал", "settings:edit:channel_username"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_operator_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("☎️ Telegram-и оператор", "settings:edit:operator_username"),),
            (("📞 Телефони оператор", "settings:edit:operator_phone"),),
            (("💬 WhatsApp-и оператор", "settings:edit:operator_whatsapp"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_texts_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("🚚 Муддати расидан TJ", "settings:edit_text:delivery_days_tj"),),
            (("🚚 Муддати расидан RU", "settings:edit_text:delivery_days_ru"),),
            (("🏙 Дохили шаҳр TJ", "settings:edit_text:delivery_inside_city_tj"),),
            (("🚕 Берун аз шаҳр TJ", "settings:edit_text:delivery_outside_city_tj"),),
            (("🏙 Дохили шаҳр RU", "settings:edit_text:delivery_inside_city_ru"),),
            (("🚕 Берун аз шаҳр RU", "settings:edit_text:delivery_outside_city_ru"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def warehouse_management_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Склад илова кардан", "admin_wh:add"),),
            (("Складро иваз кардан", "admin_wh:edit"),),
            (("Складро ғайрифаъол кардан", "admin_wh:inactive"),),
            (("Рӯйхати складҳо", "admin_wh:list"),),
        ),
    )


def admin_warehouse_city_keyboard(action: str) -> InlineKeyboardMarkup:
    city_rows = (
        (CITY_ISTARAVSHAN, CITY_DUSHANBE),
        (CITY_KHUJAND, CITY_BOKHTAR),
        (CITY_KULOB,),
    )
    return build_inline_keyboard(
        tuple(
            tuple(
                (
                    CITY_NAMES[city_key][LANG_TJ],
                    f"admin_wh:city:{action}:{city_key}",
                )
                for city_key in row
            )
            for row in city_rows
        ),
    )


def warehouse_preview_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Сабт кардан", "admin_wh:save"),),
            (("Матнро иваз кардан", "admin_wh:change_caption"),),
            (("Медиа иваз кардан", "admin_wh:change_media"),),
            (("Аз нав фиристодан", "admin_wh:resend"),),
            (("Бекор кардан", "admin_wh:cancel"),),
        ),
    )
