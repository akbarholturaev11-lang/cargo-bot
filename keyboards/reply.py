from aiogram.types import ReplyKeyboardMarkup

from keyboards.builders import build_contact_keyboard, build_reply_keyboard


USER_MENU_TJ = (
    ("🔍 Ҷустуҷӯи бор",),
    ("📦 Борҳои ман", "🧮 Ҳисоби тахминӣ"),
    ("👤 Профили ман", "🏬 Суроғаҳои склад"),
    ("💰 Нархҳо", "🚫 Манъшудаҳо"),
    ("☎️ Оператор",),
)

USER_MENU_RU = (
    ("🔍 Найти груз",),
    ("📦 Мои грузы", "🧮 Примерный расчёт"),
    ("👤 Мой профиль", "🏬 Адреса складов"),
    ("💰 Цены", "🚫 Запрещённые товары"),
    ("☎️ Оператор",),
)

ADMIN_MENU = (
    ("➕ Иловаи бор", "🔍 Ҷустуҷӯи бор"),
    ("🔄 Иваз кардани статус", "📦 Ивази гурӯҳӣ"),
    ("🇨🇳 Қабулшудаҳо", "🚚 Дар роҳ"),
    ("🏬 Расидаҳо", "🚚 Доставка"),
    ("📣 Паёми гурӯҳӣ", "⚙️ Танзимот"),
)


def user_main_menu(lang: str) -> ReplyKeyboardMarkup:
    if lang == "ru":
        return build_reply_keyboard(USER_MENU_RU)
    return build_reply_keyboard(USER_MENU_TJ)


def admin_main_menu() -> ReplyKeyboardMarkup:
    return build_reply_keyboard(ADMIN_MENU)


def phone_contact_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "📞 Отправить телефон" if lang == "ru" else "📞 Фиристодани телефон"
    return build_contact_keyboard(label)


def auth_back_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "⬅️ Назад" if lang == "ru" else "⬅️ Бозгашт"
    return build_reply_keyboard(((label,),), one_time_keyboard=True)


def auth_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    label = "📞 Отправить телефон" if lang == "ru" else "📞 Фиристодани телефон"
    back_label = "⬅️ Назад" if lang == "ru" else "⬅️ Бозгашт"
    return build_contact_keyboard(label, back_label)
