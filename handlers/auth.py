from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from keyboards.inline_user import auth_keyboard, cities_keyboard
from keyboards.reply import (
    auth_back_keyboard,
    auth_phone_keyboard,
    user_main_menu,
)
from services.normalizer import normalize_full_name
from services.users import (
    attach_telegram_account,
    create_user,
    get_user_by_id,
    get_user_by_phone,
    normalize_contact_phone,
    normalize_manual_phone,
)
from states.auth_states import AuthStates
from texts import ru, tj
from utils.constants import CITY_NAMES, LANG_RU, LANG_TJ


router = Router(name="auth")


TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


BACK_LABELS = {tj.BACK, ru.BACK}


def _is_own_contact(message: Message) -> bool:
    if message.contact is None or message.from_user is None:
        return False
    return message.contact.user_id == message.from_user.id


def _city_name(city_key: str, lang: str) -> str:
    names = CITY_NAMES.get(city_key)
    if names is None:
        return city_key
    return names[LANG_TJ]


async def _show_auth_selection_from_message(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    await state.clear()
    await state.update_data(language=lang)
    await state.set_state(AuthStates.choosing_auth_action)
    await message.answer(texts.BACK, reply_markup=ReplyKeyboardRemove())
    await message.answer(
        f"{texts.REGISTER} / {texts.LOGIN}",
        reply_markup=auth_keyboard(lang),
    )


async def _show_auth_selection_from_callback(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    await state.clear()
    await state.update_data(language=lang)
    await state.set_state(AuthStates.choosing_auth_action)
    if callback.message is not None:
        await callback.message.edit_text(
            f"{texts.REGISTER} / {texts.LOGIN}",
            reply_markup=auth_keyboard(lang),
        )
    await callback.answer()


def _contact_phone(message: Message) -> str | None:
    if message.contact is None:
        return None
    return normalize_contact_phone(message.contact.phone_number)


def _manual_phone(message: Message) -> str | None:
    if message.text is None:
        return None
    return normalize_manual_phone(message.text)


@router.callback_query(
    AuthStates.choosing_language,
    F.data.in_({"lang:tj", "lang:ru"}),
)
async def choose_language(callback: CallbackQuery, state: FSMContext) -> None:
    lang = callback.data.split(":", 1)[1]
    texts = _texts(lang)

    await state.update_data(language=lang)
    await state.set_state(AuthStates.choosing_auth_action)
    await callback.message.edit_text(
        f"{texts.REGISTER} / {texts.LOGIN}",
        reply_markup=auth_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(
    AuthStates.choosing_auth_action,
    F.data == "auth:register",
)
async def start_registration(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    await state.set_state(AuthStates.register_full_name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(texts.ASK_FULL_NAME, reply_markup=auth_back_keyboard(lang))
    await callback.answer()


@router.callback_query(AuthStates.choosing_auth_action, F.data == "auth:login")
async def start_login(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    await state.set_state(AuthStates.login_phone)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        texts.ASK_PHONE,
        reply_markup=auth_phone_keyboard(lang),
    )
    await callback.answer()


@router.message(
    AuthStates.register_full_name,
    F.text.in_(BACK_LABELS),
)
@router.message(
    AuthStates.register_phone,
    F.text.in_(BACK_LABELS),
)
@router.message(
    AuthStates.register_city,
    F.text.in_(BACK_LABELS),
)
@router.message(
    AuthStates.login_phone,
    F.text.in_(BACK_LABELS),
)
@router.message(
    AuthStates.login_full_name,
    F.text.in_(BACK_LABELS),
)
async def auth_back_message(message: Message, state: FSMContext) -> None:
    await _show_auth_selection_from_message(message, state)


@router.callback_query(
    AuthStates.register_city,
    F.data == "auth:back",
)
async def auth_back_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await _show_auth_selection_from_callback(callback, state)


@router.message(AuthStates.register_full_name, F.text)
async def register_full_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    await state.update_data(full_name=message.text.strip())
    await state.set_state(AuthStates.register_phone)
    await message.answer(texts.ASK_PHONE, reply_markup=auth_phone_keyboard(lang))


@router.message(AuthStates.register_full_name)
async def register_full_name_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    texts = _texts(data.get("language", LANG_TJ))
    await message.answer(texts.ASK_FULL_NAME)


@router.message(AuthStates.register_phone, F.contact)
async def register_phone_contact(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    if not _is_own_contact(message):
        await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))
        return

    phone = _contact_phone(message)
    if phone is None:
        await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))
        return

    await state.update_data(phone=phone)
    await state.set_state(AuthStates.register_city)
    await message.answer(texts.ASK_CITY, reply_markup=cities_keyboard(lang, include_back=True))


@router.message(AuthStates.register_phone, F.text)
async def register_phone_manual(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)
    phone = _manual_phone(message)

    if phone is None:
        await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))
        return

    await state.update_data(phone=phone)
    await state.set_state(AuthStates.register_city)
    await message.answer(texts.ASK_CITY, reply_markup=cities_keyboard(lang, include_back=True))


@router.message(AuthStates.register_phone)
async def register_phone_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)
    await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))


@router.callback_query(AuthStates.register_city, F.data.startswith("city:"))
async def register_city(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None:
        return

    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)
    city_key = callback.data.split(":", 1)[1]

    user = await create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        language=lang,
        full_name=data["full_name"],
        phone=data["phone"],
        city=_city_name(city_key, lang),
    )
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        texts.REGISTRATION_COMPLETED.format(client_code=user.client_code),
        reply_markup=user_main_menu(lang),
    )
    await callback.answer()


@router.message(AuthStates.login_phone, F.contact)
async def login_phone_contact(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    if not _is_own_contact(message):
        await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))
        return

    phone = _contact_phone(message)
    if phone is None:
        await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))
        return

    user = await get_user_by_phone(phone)
    if user is None:
        await message.answer(
            texts.PHONE_NOT_FOUND,
            reply_markup=auth_phone_keyboard(lang),
        )
        return

    lang = user.language
    texts = _texts(lang)
    await state.update_data(
        language=lang,
        login_user_id=user.id,
        phone=phone,
    )
    await state.set_state(AuthStates.login_full_name)
    await message.answer(texts.ASK_FULL_NAME, reply_markup=auth_back_keyboard(lang))


@router.message(AuthStates.login_phone, F.text)
async def login_phone_manual(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)
    phone = _manual_phone(message)

    if phone is None:
        await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))
        return

    user = await get_user_by_phone(phone)
    if user is None:
        await message.answer(
            texts.PHONE_NOT_FOUND,
            reply_markup=auth_phone_keyboard(lang),
        )
        return

    lang = user.language
    texts = _texts(lang)
    await state.update_data(
        language=lang,
        login_user_id=user.id,
        phone=phone,
    )
    await state.set_state(AuthStates.login_full_name)
    await message.answer(texts.ASK_FULL_NAME, reply_markup=auth_back_keyboard(lang))


@router.message(AuthStates.login_phone)
async def login_phone_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)
    await message.answer(texts.INVALID_PHONE, reply_markup=auth_phone_keyboard(lang))


@router.message(AuthStates.login_full_name, F.text)
async def login_full_name(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return

    data = await state.get_data()
    lang = data.get("language", LANG_TJ)
    texts = _texts(lang)

    user = await get_user_by_id(data["login_user_id"])

    if user is None:
        await state.set_state(AuthStates.login_phone)
        await message.answer(
            texts.PHONE_NOT_FOUND,
            reply_markup=auth_phone_keyboard(lang),
        )
        return

    if normalize_full_name(message.text) != user.normalized_full_name:
        await message.answer(texts.NAME_MISMATCH)
        return

    user = await attach_telegram_account(
        user.id,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )
    await state.clear()
    await message.answer(
        texts.LOGIN_SUCCESS,
        reply_markup=user_main_menu(user.language),
    )


@router.message(AuthStates.login_full_name)
async def login_full_name_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    texts = _texts(data.get("language", LANG_TJ))
    await message.answer(texts.ASK_FULL_NAME)
