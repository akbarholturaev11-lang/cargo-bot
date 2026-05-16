from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline_user import language_keyboard
from keyboards.reply import user_main_menu
from services.users import get_user_by_telegram_id
from states.auth_states import AuthStates
from texts import tj


router = Router(name="start")


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return

    user = await get_user_by_telegram_id(message.from_user.id)
    if user is not None:
        await state.clear()
        await message.answer(
            user.full_name,
            reply_markup=user_main_menu(user.language),
        )
        return

    await state.clear()
    await state.set_state(AuthStates.choosing_language)
    await message.answer(tj.CHOOSE_LANGUAGE, reply_markup=language_keyboard())
