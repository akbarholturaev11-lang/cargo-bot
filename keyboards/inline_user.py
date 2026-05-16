from aiogram.types import InlineKeyboardMarkup

from keyboards.builders import build_inline_keyboard
from utils.constants import (
    CITY_BOKHTAR,
    CITY_DUSHANBE,
    CITY_ISTARAVSHAN,
    CITY_KHUJAND,
    CITY_KULOB,
    CITY_NAMES,
    LANG_RU,
    LANG_TJ,
)


CITY_ROWS = (
    (CITY_ISTARAVSHAN, CITY_DUSHANBE),
    (CITY_KHUJAND, CITY_BOKHTAR),
    (CITY_KULOB,),
)


def language_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("Тоҷикӣ", "lang:tj"), ("Русский", "lang:ru")),
        ),
    )


def auth_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = ((("Регистрация", "auth:register"), ("Войти", "auth:login")),)
    else:
        rows = ((("Бақайдгирӣ", "auth:register"), ("Ворид шудан", "auth:login")),)
    return build_inline_keyboard(rows)


def cities_keyboard(lang: str, include_back: bool = False) -> InlineKeyboardMarkup:
    rows = tuple(
        tuple(
            (
                CITY_NAMES[city_key].get(lang, CITY_NAMES[city_key][LANG_TJ]),
                f"city:{city_key}",
            )
            for city_key in row
        )
        for row in CITY_ROWS
    )
    if include_back:
        back_label = "Назад" if lang == LANG_RU else "Бозгашт"
        rows = rows + (((back_label, "auth:back"),),)
    return build_inline_keyboard(rows)


def profile_edit_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("Изменить имя", "profile:edit_name"), ("Изменить телефон", "profile:edit_phone")),
            (("Изменить город", "profile:edit_city"), ("Изменить язык", "profile:edit_language")),
            (("Назад", "profile:back"),),
        )
    else:
        rows = (
            (("Иваз кардани ном", "profile:edit_name"), ("Иваз кардани телефон", "profile:edit_phone")),
            (("Иваз кардани шаҳр", "profile:edit_city"), ("Иваз кардани забон", "profile:edit_language")),
            (("Бозгашт", "profile:back"),),
        )
    return build_inline_keyboard(rows)


def profile_city_keyboard(lang: str) -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        tuple(
            tuple(
                (
                    CITY_NAMES[city_key].get(lang, CITY_NAMES[city_key][LANG_TJ]),
                    f"profile:city:{city_key}",
                )
                for city_key in row
            )
            for row in CITY_ROWS
        ),
    )


def profile_language_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("Тоҷикӣ", "profile:language:tj"),),
            (("Русский", "profile:language:ru"),),
            (("Назад", "profile:show"),),
        )
    else:
        rows = (
            (("Тоҷикӣ", "profile:language:tj"),),
            (("Русский", "profile:language:ru"),),
            (("Бозгашт", "profile:show"),),
        )
    return build_inline_keyboard(rows)


def calculator_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("Рассчитать по кг", "calc:kg"),),
            (("Рассчитать по кубу", "calc:cube"),),
        )
    else:
        rows = (
            (("Бо кг ҳисоб кардан", "calc:kg"),),
            (("Бо куб ҳисоб кардан", "calc:cube"),),
        )
    return build_inline_keyboard(rows)


def warehouse_city_keyboard(lang: str) -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        tuple(
            tuple(
                (
                    CITY_NAMES[city_key][LANG_TJ],
                    f"warehouse:city:{city_key}",
                )
                for city_key in row
            )
            for row in CITY_ROWS
        ),
    )


def delivery_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("Доставка", "delivery:request"),),
            (("Адрес склада 🇹🇯", "warehouse:choose"),),
        )
    else:
        rows = (
            (("Доставка", "delivery:request"),),
            (("Адреси склад 🇹🇯", "warehouse:choose"),),
        )
    return build_inline_keyboard(rows)
