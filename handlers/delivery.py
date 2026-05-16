import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.builders import build_inline_keyboard
from services.delivery import (
    create_delivery_request,
    get_arrived_parcel_for_user_by_track_code,
    get_latest_arrived_parcel_for_user,
    notify_admins_about_delivery_request,
)
from services.settings import get_bool_setting, get_setting
from services.users import get_user_by_telegram_id
from states.delivery_states import DeliveryStates
from texts import tj


router = Router(name="delivery")


def _confirm_keyboard():
    return build_inline_keyboard(
        (
            (("Тасдиқ", "delivery:confirm"),),
            (("Бекор кардан", "delivery:cancel"),),
        ),
    )


def _extract_track_code(text: str | None) -> str | None:
    if not text:
        return None

    match = re.search(r"Трек-код:\s*(.+)", text)
    if match is None:
        return None
    return match.group(1).strip()


def _format_terms(inside_city: str, outside_city: str) -> str:
    return (
        "Хизматрасонии доставка\n\n"
        f"{inside_city}\n\n"
        f"{outside_city}\n\n"
        "Лутфан адреси худро равон кунед:"
    )


def _format_confirmation(data: dict) -> str:
    return (
        "Дархости доставкаро тасдиқ кунед\n\n"
        f"Трек-код: {data['track_code']}\n"
        f"Ном: {data['full_name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Склад: {data['destination_city']}\n"
        f"Адрес: {data['delivery_address']}"
    )


@router.callback_query(F.data == "delivery:request")
async def start_delivery_request(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None:
        await callback.answer()
        return

    delivery_enabled = await get_bool_setting("delivery_enabled", False)
    if not delivery_enabled:
        if callback.message is not None:
            await callback.message.answer(
                "Ҳозирча хизматрасонии доставка фаъол нест.\n"
                "Лутфан борро аз склад гирифта баред.",
            )
        await callback.answer()
        return

    track_code = _extract_track_code(callback.message.text if callback.message else None)
    parcel = None
    if track_code is not None:
        parcel = await get_arrived_parcel_for_user_by_track_code(
            user_id=user.id,
            track_code=track_code,
        )
    if parcel is None:
        parcel = await get_latest_arrived_parcel_for_user(user.id)

    if parcel is None:
        if callback.message is not None:
            await callback.message.answer("Бори расида барои доставка ёфт нашуд.")
        await callback.answer()
        return

    inside_city = await get_setting(
        "delivery_inside_city_tj",
        "Дохили шаҳр: 15 сомонӣ",
    )
    outside_city = await get_setting(
        "delivery_outside_city_tj",
        "Берун аз шаҳр: ба таксӣ равон мекунем, ҳаққи таксӣ алоҳида ҳисоб мешавад.",
    )

    await state.set_state(DeliveryStates.waiting_for_address)
    await state.update_data(
        parcel_id=parcel.id,
        track_code=parcel.track_code,
        full_name=user.full_name,
        phone=user.phone,
        destination_city=parcel.destination_city,
    )
    if callback.message is not None:
        await callback.message.answer(_format_terms(inside_city or "", outside_city or ""))
    await callback.answer()


@router.message(DeliveryStates.waiting_for_address, F.text)
async def delivery_address_received(message: Message, state: FSMContext) -> None:
    address = message.text.strip()
    if not address:
        await message.answer("Лутфан адреси худро равон кунед:")
        return

    await state.update_data(delivery_address=address)
    await state.set_state(DeliveryStates.confirming)
    data = await state.get_data()
    await message.answer(_format_confirmation(data), reply_markup=_confirm_keyboard())


@router.message(DeliveryStates.waiting_for_address)
async def delivery_address_invalid(message: Message) -> None:
    await message.answer("Лутфан адреси худро равон кунед:")


@router.callback_query(DeliveryStates.confirming, F.data == "delivery:cancel")
async def cancel_delivery(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if callback.message is not None:
        await callback.message.edit_text("Дархости доставка бекор карда шуд.")
    await callback.answer()


@router.callback_query(DeliveryStates.confirming, F.data == "delivery:confirm")
async def confirm_delivery(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None:
        await state.clear()
        await callback.answer()
        return

    data = await state.get_data()
    parcel = await get_arrived_parcel_for_user_by_track_code(
        user_id=user.id,
        track_code=data["track_code"],
    )
    if parcel is None:
        await state.clear()
        if callback.message is not None:
            await callback.message.edit_text("Бори расида барои доставка ёфт нашуд.")
        await callback.answer()
        return

    request = await create_delivery_request(
        parcel=parcel,
        user=user,
        delivery_address=data["delivery_address"],
    )
    bot = callback.message.bot if callback.message is not None else callback.bot
    await notify_admins_about_delivery_request(bot, request, user)
    await state.clear()
    if callback.message is not None:
        await callback.message.edit_text(tj.DELIVERY_REQUEST_ACCEPTED)
    await callback.answer()
