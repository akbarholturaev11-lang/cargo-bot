from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.user_menu import get_current_user
from keyboards.inline_user import calculator_keyboard
from services.calculator import (
    calculate_total,
    format_decimal,
    get_price_per_cube,
    get_price_per_kg,
    parse_positive_decimal,
)
from services.settings import get_setting
from services.users import get_user_by_telegram_id
from states.calculator_states import CalculatorStates
from texts import ru, tj
from utils.constants import LANG_RU, LANG_TJ


router = Router(name="calculator")


CALCULATOR_MENU_LABELS = {tj.MENU_CALCULATOR, ru.MENU_CALCULATOR}
TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


async def _current_language(message: Message) -> str:
    user = await get_current_user(message)
    if user is None:
        return LANG_TJ
    return user.language


def _format_result(
    *,
    amount: Decimal,
    price: Decimal,
    total: Decimal,
    lang: str,
    mode: str,
) -> str:
    texts = _texts(lang)
    template = (
        texts.CALCULATOR_KG_RESULT
        if mode == "kg"
        else texts.CALCULATOR_CUBE_RESULT
    )
    return template.format(
        amount=format_decimal(amount),
        price=format_decimal(price),
        total=format_decimal(total),
    )


def _calculator_intro(lang: str) -> str:
    if lang == LANG_RU:
        return "🧮 Примерный расчёт\n\nКаким способом рассчитать?"
    return "🧮 Ҳисоби тахминӣ\n\nБо кадом усул ҳисоб мекунед?"


async def _edit_calculator_message(callback: CallbackQuery, text: str) -> None:
    if callback.message is None:
        return

    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=None)
        return

    await callback.message.edit_text(text)


@router.message(F.text.in_(CALCULATOR_MENU_LABELS))
async def show_calculator(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    await state.clear()
    intro_text = _calculator_intro(user.language)
    image_file_id = await get_setting("calculator_image_file_id", "")
    if image_file_id:
        await message.answer_photo(
            photo=image_file_id,
            caption=intro_text,
            reply_markup=calculator_keyboard(user.language),
        )
        return

    await message.answer(intro_text, reply_markup=calculator_keyboard(user.language))


@router.callback_query(F.data == "calc:kg")
async def choose_kg(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return

    user = await get_user_by_telegram_id(callback.from_user.id)
    lang = user.language if user is not None else LANG_TJ

    await state.set_state(CalculatorStates.waiting_for_kg)
    await _edit_calculator_message(callback, _texts(lang).CALCULATOR_ASK_KG)
    await callback.answer()


@router.callback_query(F.data == "calc:cube")
async def choose_cube(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None:
        await callback.answer()
        return

    user = await get_user_by_telegram_id(callback.from_user.id)
    lang = user.language if user is not None else LANG_TJ

    await state.set_state(CalculatorStates.waiting_for_cube)
    await _edit_calculator_message(callback, _texts(lang).CALCULATOR_ASK_CUBE)
    await callback.answer()


@router.message(CalculatorStates.waiting_for_kg, F.text)
async def calculate_by_kg(message: Message, state: FSMContext) -> None:
    lang = await _current_language(message)
    amount = parse_positive_decimal(message.text)
    if amount is None:
        await message.answer(_texts(lang).CALCULATOR_INVALID_NUMBER)
        return

    price = await get_price_per_kg()
    total = calculate_total(amount, price)
    await state.clear()
    await message.answer(
        _format_result(
            amount=amount,
            price=price,
            total=total,
            lang=lang,
            mode="kg",
        ),
    )


@router.message(CalculatorStates.waiting_for_cube, F.text)
async def calculate_by_cube(message: Message, state: FSMContext) -> None:
    lang = await _current_language(message)
    amount = parse_positive_decimal(message.text)
    if amount is None:
        await message.answer(_texts(lang).CALCULATOR_INVALID_NUMBER)
        return

    price = await get_price_per_cube()
    total = calculate_total(amount, price)
    await state.clear()
    await message.answer(
        _format_result(
            amount=amount,
            price=price,
            total=total,
            lang=lang,
            mode="cube",
        ),
    )


@router.message(CalculatorStates.waiting_for_kg)
async def calculate_by_kg_invalid(message: Message) -> None:
    lang = await _current_language(message)
    await message.answer(_texts(lang).CALCULATOR_INVALID_NUMBER)


@router.message(CalculatorStates.waiting_for_cube)
async def calculate_by_cube_invalid(message: Message) -> None:
    lang = await _current_language(message)
    await message.answer(_texts(lang).CALCULATOR_INVALID_NUMBER)
