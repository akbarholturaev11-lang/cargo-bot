from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline_admin import (
    admin_warehouse_city_keyboard,
    warehouse_management_keyboard,
    warehouse_preview_keyboard,
)
from services.warehouses import (
    list_warehouses,
    save_active_warehouse,
    set_warehouse_inactive,
)
from states.admin_warehouse_states import AdminWarehouseStates
from utils.constants import CITY_NAMES, LANG_TJ
from utils.validators import is_admin


router = Router(name="admin_warehouses")


PHOTO_CAPTION_PROMPT = (
    "Сурати суроғаро бо матн дар як паём фиристед.\n"
    "Мисол:\n"
    "收货人：Sandy\n"
    "联系电话：15699156115\n"
    "地址：浙江省义乌市青口后湖小区5栋5单元"
)


def _is_admin_message(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _is_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)


def _city_name(city_key: str) -> str:
    return CITY_NAMES[city_key][LANG_TJ]


async def _show_preview(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(AdminWarehouseStates.confirming)
    await message.answer_photo(
        photo=data["image_file_id"],
        caption=data["address_caption"],
        reply_markup=warehouse_preview_keyboard(),
    )


@router.callback_query(F.data == "settings:warehouses")
async def show_warehouse_settings(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    if callback.message is not None:
        await callback.message.edit_text(
            "Складҳо",
            reply_markup=warehouse_management_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data.in_({"admin_wh:add", "admin_wh:edit"}))
async def start_add_or_edit_warehouse(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    action = callback.data.rsplit(":", 1)[1]
    await state.clear()
    await state.update_data(action=action)
    await state.set_state(AdminWarehouseStates.choosing_city)

    if callback.message is not None:
        await callback.message.edit_text(
            "Шаҳрро интихоб кунед.",
            reply_markup=admin_warehouse_city_keyboard(action),
        )
    await callback.answer()


@router.callback_query(F.data == "admin_wh:inactive")
async def start_inactive_warehouse(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    await state.set_state(AdminWarehouseStates.choosing_inactive_city)
    if callback.message is not None:
        await callback.message.edit_text(
            "Ғайрифаъол кардан: шаҳрро интихоб кунед.",
            reply_markup=admin_warehouse_city_keyboard("inactive"),
        )
    await callback.answer()


@router.callback_query(F.data == "admin_wh:list")
async def list_admin_warehouses(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    warehouses = await list_warehouses()
    if not warehouses:
        text = "Склад сабт нашудааст."
    else:
        lines = ["Рӯйхати складҳо:"]
        for warehouse in warehouses:
            status = "фаъол" if warehouse.is_active else "ғайрифаъол"
            lines.append(
                f"{warehouse.city_name_tj}: {status} · ID {warehouse.id}",
            )
        text = "\n".join(lines)

    if callback.message is not None:
        await callback.message.edit_text(
            text,
            reply_markup=warehouse_management_keyboard(),
        )
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.choosing_city,
    F.data.startswith("admin_wh:city:"),
)
async def choose_warehouse_city(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer()
        return

    city_key = parts[3]
    if city_key not in CITY_NAMES:
        await callback.answer()
        return

    await state.update_data(city_key=city_key, city_name=_city_name(city_key))
    await state.set_state(AdminWarehouseStates.waiting_for_photo_caption)
    if callback.message is not None:
        await callback.message.edit_text(PHOTO_CAPTION_PROMPT)
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.choosing_inactive_city,
    F.data.startswith("admin_wh:city:inactive:"),
)
async def inactive_warehouse_city(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    city_key = callback.data.rsplit(":", 1)[1]
    if city_key not in CITY_NAMES:
        await callback.answer()
        return

    count = await set_warehouse_inactive(city_key)
    await state.clear()
    if callback.message is not None:
        await callback.message.edit_text(
            f"{_city_name(city_key)} ғайрифаъол шуд. Сабтҳо: {count}",
            reply_markup=warehouse_management_keyboard(),
        )
    await callback.answer()


@router.message(AdminWarehouseStates.waiting_for_photo_caption, F.photo)
async def receive_warehouse_photo_caption(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    if not message.caption:
        await message.answer("Матн лозим аст. Суратро бо матн фиристед.")
        return

    await state.update_data(
        image_file_id=message.photo[-1].file_id,
        address_caption=message.caption,
    )
    await _show_preview(message, state)


@router.message(AdminWarehouseStates.waiting_for_photo_caption)
async def receive_warehouse_photo_caption_invalid(message: Message) -> None:
    if not _is_admin_message(message):
        return

    await message.answer(PHOTO_CAPTION_PROMPT)


@router.callback_query(AdminWarehouseStates.confirming, F.data == "admin_wh:save")
async def save_warehouse(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    data = await state.get_data()
    warehouse = await save_active_warehouse(
        city_key=data["city_key"],
        image_file_id=data["image_file_id"],
        address_caption=data["address_caption"],
    )
    await state.clear()
    if callback.message is not None:
        await callback.message.edit_caption(
            caption=(
                "Склад сабт шуд.\n"
                f"Шаҳр: {warehouse.city_name_tj}\n"
                f"Статус: фаъол"
            ),
            reply_markup=None,
        )
    await callback.answer()


@router.callback_query(
    AdminWarehouseStates.confirming,
    F.data == "admin_wh:change_caption",
)
async def change_warehouse_caption(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.set_state(AdminWarehouseStates.waiting_for_caption)
    if callback.message is not None:
        await callback.message.answer("Матни навро фиристед.")
    await callback.answer()


@router.message(AdminWarehouseStates.waiting_for_caption, F.text)
async def receive_new_caption(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.update_data(address_caption=message.text)
    await _show_preview(message, state)


@router.callback_query(
    AdminWarehouseStates.confirming,
    F.data == "admin_wh:change_photo",
)
async def change_warehouse_photo(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.set_state(AdminWarehouseStates.waiting_for_photo)
    if callback.message is not None:
        await callback.message.answer("Сурати навро фиристед.")
    await callback.answer()


@router.message(AdminWarehouseStates.waiting_for_photo, F.photo)
async def receive_new_photo(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    data = await state.get_data()
    caption = message.caption or data["address_caption"]
    await state.update_data(
        image_file_id=message.photo[-1].file_id,
        address_caption=caption,
    )
    await _show_preview(message, state)


@router.callback_query(AdminWarehouseStates.confirming, F.data == "admin_wh:resend")
async def resend_warehouse_block(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.set_state(AdminWarehouseStates.waiting_for_photo_caption)
    if callback.message is not None:
        await callback.message.answer(PHOTO_CAPTION_PROMPT)
    await callback.answer()


@router.callback_query(F.data == "admin_wh:cancel")
async def cancel_warehouse_flow(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    if callback.message is not None:
        if callback.message.photo:
            await callback.message.edit_caption("Амалиёт бекор карда шуд.")
        else:
            await callback.message.edit_text("Амалиёт бекор карда шуд.")
    await callback.answer()
