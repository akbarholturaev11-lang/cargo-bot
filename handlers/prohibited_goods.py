from aiogram import F, Router
from aiogram.types import Message

from services.users import get_current_user
from texts import ru, tj
from utils.constants import LANG_RU, LANG_TJ

router = Router(name="prohibited_goods")


def _texts(lang: str):
    return ru if lang == LANG_RU else tj


PROHIBITED_LABELS = {
    tj.MENU_PROHIBITED,
    ru.MENU_PROHIBITED,
}


@router.message(F.text.in_(PROHIBITED_LABELS))
async def prohibited_goods_handler(message: Message) -> None:
    user = await get_current_user(message)

    lang = getattr(user, "language", LANG_TJ) if user else LANG_TJ
    texts = _texts(lang)

    await message.answer(texts.PROHIBITED_GOODS)
