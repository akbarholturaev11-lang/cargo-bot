from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards.builders import build_inline_keyboard
from keyboards.reply import ADMIN_MENU
from services.normalizer import normalize_track_code
from services.notifications import notify_arrival_destination
from services.parcels import (
    get_parcel_with_user,
    get_parcel_with_user_by_normalized_track_code,
    mark_arrival_notified,
    update_parcel_status,
)
from texts.status import format_status
from utils.constants import (
    LANG_TJ,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_CODES,
    STATUS_ON_THE_WAY,
)
from utils.validators import is_admin


router = Router(name="admin_status")


ADMIN_SEARCH_LABEL = ADMIN_MENU[0][1]
ADMIN_STATUS_UPDATE_LABEL = ADMIN_MENU[1][0]


class AdminParcelStatusStates(StatesGroup):
    waiting_for_search_track_code = State()
    waiting_for_status_track_code = State()


def _is_admin_message(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _is_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)


def _format_date(value: datetime | date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y")


def _format_parcel(parcel) -> str:
    user = parcel.user
    return (
        "Маълумоти бор\n\n"
        f"Трек-код: {parcel.track_code}\n"
        f"Ном: {user.full_name}\n"
        f"Телефон: {user.phone}\n"
        f"Коди мизоҷ: {parcel.client_code}\n"
        f"Склад: {parcel.destination_city}\n"
        f"Статус: {format_status(parcel.status_code, parcel.destination_city, LANG_TJ)}\n"
        f"Санаи қабул: {_format_date(parcel.received_china_at)}"
    )


def _status_keyboard(parcel) -> object:
    return build_inline_keyboard(
        (
            (
                (
                    "Дар склади Чин қабул шуд",
                    f"admin_status:set:{parcel.id}:{STATUS_CHINA_RECEIVED}",
                ),
            ),
            (
                (
                    "Дар роҳ аст",
                    f"admin_status:set:{parcel.id}:{STATUS_ON_THE_WAY}",
                ),
            ),
            (
                (
                    format_status(
                        STATUS_ARRIVED_DESTINATION,
                        parcel.destination_city,
                        LANG_TJ,
                    ),
                    f"admin_status:set:{parcel.id}:{STATUS_ARRIVED_DESTINATION}",
                ),
            ),
        ),
    )


async def _find_parcel_by_message_track_code(message: Message):
    normalized_track_code = normalize_track_code(message.text or "")
    if not normalized_track_code:
        return None
    return await get_parcel_with_user_by_normalized_track_code(normalized_track_code)


@router.message(F.text == ADMIN_SEARCH_LABEL)
async def start_admin_search(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.clear()
    await state.set_state(AdminParcelStatusStates.waiting_for_search_track_code)
    await message.answer("Трек-кодро ворид кунед.")


@router.message(AdminParcelStatusStates.waiting_for_search_track_code, F.text)
async def admin_search_parcel(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    parcel = await _find_parcel_by_message_track_code(message)
    await state.clear()
    if parcel is None:
        await message.answer("Ин трек-код ёфт нашуд.")
        return

    await message.answer(_format_parcel(parcel))


@router.message(F.text == ADMIN_STATUS_UPDATE_LABEL)
async def start_status_update(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.clear()
    await state.set_state(AdminParcelStatusStates.waiting_for_status_track_code)
    await message.answer("Трек-кодро ворид кунед.")


@router.message(AdminParcelStatusStates.waiting_for_status_track_code, F.text)
async def status_update_find_parcel(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    parcel = await _find_parcel_by_message_track_code(message)
    await state.clear()
    if parcel is None:
        await message.answer("Ин трек-код ёфт нашуд.")
        return

    await message.answer(
        _format_parcel(parcel),
        reply_markup=_status_keyboard(parcel),
    )


@router.callback_query(F.data.startswith("admin_status:set:"))
async def set_single_status(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer()
        return

    try:
        parcel_id = int(parts[2])
    except ValueError:
        await callback.answer()
        return

    status_code = parts[3]
    if status_code not in STATUS_CODES:
        await callback.answer()
        return

    before_update = await get_parcel_with_user(parcel_id)
    if before_update is None:
        if callback.message is not None:
            await callback.message.edit_text("Ин трек-код ёфт нашуд.")
        await callback.answer()
        return

    parcel = await update_parcel_status(parcel_id, status_code)
    if parcel is None:
        if callback.message is not None:
            await callback.message.edit_text("Ин трек-код ёфт нашуд.")
        await callback.answer()
        return

    notified = False
    if (
        status_code == STATUS_ARRIVED_DESTINATION
        and before_update.arrival_notified_at is None
    ):
        bot = callback.message.bot if callback.message is not None else callback.bot
        notified = await notify_arrival_destination(bot, parcel.user, parcel)
        if notified:
            await mark_arrival_notified(parcel.id)
            parcel = await get_parcel_with_user(parcel.id) or parcel

    text = _format_parcel(parcel) + "\n\nСтатус нав шуд."
    if status_code == STATUS_ARRIVED_DESTINATION and notified:
        text += "\nБа мизоҷ хабар фиристода шуд."

    if callback.message is not None:
        await callback.message.edit_text(text, reply_markup=_status_keyboard(parcel))
    await callback.answer()
