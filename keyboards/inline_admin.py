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
            (("Нархлар", "settings:prices"),),
            (("Ҳисоблаш", "settings:calculation"),),
            (("Доставка", "settings:delivery"),),
            (("Складлар", "settings:warehouses"),),
            (("Канал", "settings:channel"),),
            (("Оператор", "settings:operator"),),
            (("Матнлар", "settings:texts"),),
            (("Бозгашт", "settings:back"),),
        ),
    )


def settings_prices_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("price_per_kg_tjs", "settings:edit:price_per_kg_tjs"),),
            (("price_per_cube_tjs", "settings:edit:price_per_cube_tjs"),),
            (("delivery_days_tj", "settings:edit:delivery_days_tj"),),
            (("delivery_days_ru", "settings:edit:delivery_days_ru"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_calculation_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("price_per_kg_tjs", "settings:edit:price_per_kg_tjs"),),
            (("price_per_cube_tjs", "settings:edit:price_per_cube_tjs"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_delivery_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("delivery_enabled ON/OFF", "settings:toggle:delivery_enabled"),),
            (("delivery_inside_city_tj", "settings:edit:delivery_inside_city_tj"),),
            (("delivery_outside_city_tj", "settings:edit:delivery_outside_city_tj"),),
            (("delivery_inside_city_ru", "settings:edit:delivery_inside_city_ru"),),
            (("delivery_outside_city_ru", "settings:edit:delivery_outside_city_ru"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_channel_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("require_channel_join ON/OFF", "settings:toggle:require_channel_join"),),
            (("channel_username", "settings:edit:channel_username"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_operator_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("operator_username", "settings:edit:operator_username"),),
            (("operator_phone", "settings:edit:operator_phone"),),
            (("operator_whatsapp", "settings:edit:operator_whatsapp"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def settings_texts_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("delivery_days_tj", "settings:edit_text:delivery_days_tj"),),
            (("delivery_days_ru", "settings:edit_text:delivery_days_ru"),),
            (("delivery_inside_city_tj", "settings:edit_text:delivery_inside_city_tj"),),
            (("delivery_outside_city_tj", "settings:edit_text:delivery_outside_city_tj"),),
            (("delivery_inside_city_ru", "settings:edit_text:delivery_inside_city_ru"),),
            (("delivery_outside_city_ru", "settings:edit_text:delivery_outside_city_ru"),),
            (("Бозгашт", "settings:main"),),
        ),
    )


def warehouse_management_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Склад қўшиш", "admin_wh:add"),),
            (("Складни ўзгартириш", "admin_wh:edit"),),
            (("Складни inactive қилиш", "admin_wh:inactive"),),
            (("Складлар рўйхати", "admin_wh:list"),),
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
            (("Суратро иваз кардан", "admin_wh:change_photo"),),
            (("Аз нав фиристодан", "admin_wh:resend"),),
            (("Бекор кардан", "admin_wh:cancel"),),
        ),
    )
