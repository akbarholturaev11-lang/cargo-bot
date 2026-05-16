from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards.builders import build_inline_keyboard
from keyboards.reply import ADMIN_MENU
from services.delivery import (
    format_delivery_request_for_admin,
    get_delivery_request,
    get_delivery_requests,
    update_delivery_status,
)
from utils.constants import (
    DELIVERY_STATUS_ACCEPTED,
    DELIVERY_STATUS_CANCELLED,
    DELIVERY_STATUS_DELIVERED,
    DELIVERY_STATUS_ON_DELIVERY,
    DELIVERY_STATUSES,
)
from utils.validators import is_admin


router = Router(name="admin_delivery")


ADMIN_DELIVERY_LABEL = ADMIN_MENU[3][1]


def _is_admin_message(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _is_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)


def _requests_keyboard(requests):
    rows = tuple(
        (
            (
                f"ID {request.id} · {request.track_code}",
                f"admin_delivery:view:{request.id}",
            ),
        )
        for request in requests
    )
    return build_inline_keyboard(rows)


def _status_keyboard(request_id: int):
    return build_inline_keyboard(
        (
            (("Қабул шуд", f"admin_delivery:set:{request_id}:{DELIVERY_STATUS_ACCEPTED}"),),
            (("Дар доставка", f"admin_delivery:set:{request_id}:{DELIVERY_STATUS_ON_DELIVERY}"),),
            (("Расонида шуд", f"admin_delivery:set:{request_id}:{DELIVERY_STATUS_DELIVERED}"),),
            (("Бекор шуд", f"admin_delivery:set:{request_id}:{DELIVERY_STATUS_CANCELLED}"),),
        ),
    )


@router.message(F.text == ADMIN_DELIVERY_LABEL)
async def show_delivery_requests(message: Message) -> None:
    if not _is_admin_message(message):
        return

    requests = await get_delivery_requests()
    if not requests:
        await message.answer("Дархости доставка нест.")
        return

    await message.answer(
        "Дархостҳои доставка:",
        reply_markup=_requests_keyboard(requests),
    )


@router.callback_query(F.data.startswith("admin_delivery:view:"))
async def view_delivery_request(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    try:
        request_id = int(callback.data.rsplit(":", 1)[1])
    except ValueError:
        await callback.answer()
        return

    request = await get_delivery_request(request_id)
    if request is None:
        if callback.message is not None:
            await callback.message.edit_text("Дархост ёфт нашуд.")
        await callback.answer()
        return

    if callback.message is not None:
        await callback.message.edit_text(
            format_delivery_request_for_admin(request, request.user),
            reply_markup=_status_keyboard(request.id),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delivery:set:"))
async def set_delivery_status(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer()
        return

    try:
        request_id = int(parts[2])
    except ValueError:
        await callback.answer()
        return

    status = parts[3]
    if status not in DELIVERY_STATUSES:
        await callback.answer()
        return

    request = await update_delivery_status(
        request_id=request_id,
        status=status,
        admin_id=callback.from_user.id,
    )
    if request is None:
        if callback.message is not None:
            await callback.message.edit_text("Дархост ёфт нашуд.")
        await callback.answer()
        return

    request = await get_delivery_request(request_id)
    if callback.message is not None and request is not None:
        await callback.message.edit_text(
            format_delivery_request_for_admin(request, request.user),
            reply_markup=_status_keyboard(request.id),
        )
    await callback.answer("Статус нав шуд.")
