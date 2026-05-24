from __future__ import annotations

from datetime import datetime, date
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy import distinct, func, select

from database.db import async_session
from database.models import Parcel, User
from keyboards.reply import ADMIN_MENU
from states.admin_broadcast_states import AdminBroadcastStates
from services.normalizer import normalize_track_code
from texts.status import format_status
from utils.constants import (
    LANG_TJ,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
    STATUS_RECEIVED,
)
from utils.validators import is_admin


router = Router(name="admin_broadcast")

BROADCAST_LABEL = ADMIN_MENU[4][0]


def _kb(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
            for row in rows
        ]
    )


def broadcast_language_keyboard() -> InlineKeyboardMarkup:
    return _kb(
        [
            [("🇹🇯 Тоҷикӣ", "broadcast:language:tj")],
            [("🇷🇺 Русӣ", "broadcast:language:ru")],
            [("❌ Бекор кардан", "broadcast:cancel")],
        ]
    )


def broadcast_main_keyboard() -> InlineKeyboardMarkup:
    return _kb(
        [
            [("👥 Ба ҳама user’ҳо", "broadcast:filter:all")],
            [("📦 Аз рӯи статус", "broadcast:filter:status")],
            [("📅 Аз рӯи сана", "broadcast:filter:date")],
            [("🆔 Ба як user бо Telegram ID", "broadcast:filter:telegram_id")],
            [("🔢 Бо трек-код", "broadcast:filter:track_code")],
            [("❌ Бекор кардан", "broadcast:cancel")],
        ]
    )


def broadcast_status_keyboard() -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                (
                    format_status(STATUS_CHINA_RECEIVED, "", LANG_TJ),
                    f"broadcast:status:{STATUS_CHINA_RECEIVED}",
                )
            ],
            [
                (
                    format_status(STATUS_ON_THE_WAY, "", LANG_TJ),
                    f"broadcast:status:{STATUS_ON_THE_WAY}",
                )
            ],
            [
                (
                    format_status(STATUS_ARRIVED_DESTINATION, "", LANG_TJ),
                    f"broadcast:status:{STATUS_ARRIVED_DESTINATION}",
                )
            ],
            [
                (
                    format_status(STATUS_RECEIVED, "", LANG_TJ),
                    f"broadcast:status:{STATUS_RECEIVED}",
                )
            ],
            [("⬅️ Бозгашт", "broadcast:back")],
        ]
    )


def broadcast_date_field_keyboard() -> InlineKeyboardMarkup:
    return _kb(
        [
            [("🇨🇳 Санаи қабул дар Чин", "broadcast:date_field:received_china_at")],
            [("📦 Санаи партия", "broadcast:date_field:batch_date")],
            [("🕒 Санаи сабт", "broadcast:date_field:created_at")],
            [("⬅️ Бозгашт", "broadcast:back")],
        ]
    )


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return _kb(
        [
            [("✅ Фиристодан", "broadcast:send")],
            [("❌ Бекор кардан", "broadcast:cancel")],
        ]
    )


def _parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


async def _target_telegram_ids(data: dict[str, Any]) -> list[int]:
    filter_type = data.get("filter_type")
    broadcast_language = data.get("broadcast_language")

    if broadcast_language not in {"tj", "ru"}:
        return []

    async with async_session() as session:
        if filter_type == "all":
            result = await session.execute(
                select(User.telegram_id)
                .where(User.telegram_id.is_not(None))
                .where(User.status == "active")
                .where(User.language == broadcast_language)
            )
            return [int(x) for x in result.scalars().all() if x]

        if filter_type == "telegram_id":
            telegram_id = data.get("telegram_id")
            if not telegram_id:
                return []
            result = await session.execute(
                select(User.telegram_id)
                .where(User.telegram_id == int(telegram_id))
                .where(User.language == broadcast_language)
            )
            return [int(x) for x in result.scalars().all() if x]

        if filter_type == "track_code":
            track_code = data.get("track_code")
            if not track_code:
                return []

            normalized_track_code = normalize_track_code(track_code)

            result = await session.execute(
                select(User.telegram_id)
                .join(Parcel, Parcel.user_id == User.id)
                .where(Parcel.normalized_track_code == normalized_track_code)
                .where(User.telegram_id.is_not(None))
                .where(User.language == broadcast_language)
            )
            return [int(x) for x in result.scalars().all() if x]

        if filter_type == "status":
            status_code = data.get("status_code")
            result = await session.execute(
                select(distinct(User.telegram_id))
                .join(Parcel, Parcel.user_id == User.id)
                .where(Parcel.status_code == status_code)
                .where(User.telegram_id.is_not(None))
                .where(User.status == "active")
                .where(User.language == broadcast_language)
            )
            return [int(x) for x in result.scalars().all() if x]

        if filter_type == "date":
            field = data.get("date_field")
            target_date = data.get("target_date")

            if not field or not target_date:
                return []

            if isinstance(target_date, str):
                parsed = _parse_date(target_date)
                if parsed is None:
                    return []
                target_date = parsed

            if field == "received_china_at":
                condition = func.date(Parcel.received_china_at) == target_date
            elif field == "batch_date":
                condition = Parcel.batch_date == target_date
            elif field == "created_at":
                condition = func.date(Parcel.created_at) == target_date
            else:
                return []

            result = await session.execute(
                select(distinct(User.telegram_id))
                .join(Parcel, Parcel.user_id == User.id)
                .where(condition)
                .where(User.telegram_id.is_not(None))
                .where(User.status == "active")
                .where(User.language == broadcast_language)
            )
            return [int(x) for x in result.scalars().all() if x]

    return []


def _filter_title(data: dict[str, Any]) -> str:
    filter_type = data.get("filter_type")

    if filter_type == "all":
        return "Ҳама user’ҳо"

    if filter_type == "telegram_id":
        return f"Telegram ID: {data.get('telegram_id')}"

    if filter_type == "track_code":
        return f"Трек-код: {data.get('track_code')}"

    if filter_type == "status":
        return f"Статус: {format_status(data.get('status_code', ''), '', LANG_TJ)}"

    if filter_type == "date":
        field_names = {
            "received_china_at": "Санаи қабул дар Чин",
            "batch_date": "Санаи партия",
            "created_at": "Санаи сабт",
        }
        field = field_names.get(data.get("date_field"), data.get("date_field"))
        return f"{field}: {data.get('target_date')}"

    return "Номаълум"


async def _save_content(message: Message, state: FSMContext) -> bool:
    content: dict[str, Any] = {}

    if message.text:
        content = {
            "type": "text",
            "text": message.text,
        }

    elif message.photo:
        content = {
            "type": "photo",
            "file_id": message.photo[-1].file_id,
            "caption": message.caption or "",
        }

    elif message.video:
        content = {
            "type": "video",
            "file_id": message.video.file_id,
            "caption": message.caption or "",
        }

    elif message.voice:
        content = {
            "type": "voice",
            "file_id": message.voice.file_id,
            "caption": message.caption or "",
        }

    else:
        return False

    await state.update_data(content=content)
    return True


async def _send_content(bot, chat_id: int, content: dict[str, Any]) -> None:
    content_type = content.get("type")

    if content_type == "text":
        await bot.send_message(chat_id=chat_id, text=content.get("text", ""))
        return

    if content_type == "photo":
        await bot.send_photo(
            chat_id=chat_id,
            photo=content.get("file_id"),
            caption=content.get("caption") or None,
        )
        return

    if content_type == "video":
        await bot.send_video(
            chat_id=chat_id,
            video=content.get("file_id"),
            caption=content.get("caption") or None,
        )
        return

    if content_type == "voice":
        await bot.send_voice(
            chat_id=chat_id,
            voice=content.get("file_id"),
            caption=content.get("caption") or None,
        )
        return

    raise ValueError("Unsupported broadcast content type")


async def _preview_content(message: Message, content: dict[str, Any]) -> None:
    await message.answer("👀 <b>Preview:</b>")

    content_type = content.get("type")

    if content_type == "text":
        await message.answer(content.get("text", ""))
    elif content_type == "photo":
        await message.answer_photo(
            photo=content.get("file_id"),
            caption=content.get("caption") or None,
        )
    elif content_type == "video":
        await message.answer_video(
            video=content.get("file_id"),
            caption=content.get("caption") or None,
        )
    elif content_type == "voice":
        await message.answer_voice(
            voice=content.get("file_id"),
            caption=content.get("caption") or None,
        )


@router.message(F.text.in_({BROADCAST_LABEL, "Паёми гурӯҳӣ"}))
async def open_broadcast_menu(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        return

    await state.clear()
    await state.set_state(AdminBroadcastStates.choosing_language)

    await message.answer(
        "📣 <b>Паёми гурӯҳӣ</b>\n\n"
        "<blockquote>Аввал забони user’ҳоро интихоб кунед.</blockquote>",
        reply_markup=broadcast_language_keyboard(),
    )



@router.callback_query(F.data.startswith("broadcast:language:"))
async def choose_broadcast_language(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    lang = callback.data.split(":")[-1]
    if lang not in {"tj", "ru"}:
        await callback.answer("Нодуруст", show_alert=True)
        return

    await state.update_data(broadcast_language=lang)
    await state.set_state(AdminBroadcastStates.choosing_filter)

    lang_text = "🇹🇯 Тоҷикӣ" if lang == "tj" else "🇷🇺 Русӣ"

    await callback.message.edit_text(
        "📣 <b>Паёми гурӯҳӣ</b>\n\n"
        f"<blockquote>Забон: <b>{lang_text}</b>\n"
        "Акнун филтрро интихоб кунед.</blockquote>",
        reply_markup=broadcast_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:back")
async def broadcast_back(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    await state.set_state(AdminBroadcastStates.choosing_language)
    await callback.message.edit_text(
        "📣 <b>Паёми гурӯҳӣ</b>\n\n"
        "<blockquote>Аввал забони user’ҳоро интихоб кунед.</blockquote>",
        reply_markup=broadcast_language_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "broadcast:cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    await state.clear()
    await callback.message.edit_text("❌ <b>Паёми гурӯҳӣ бекор шуд.</b>")
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:filter:"))
async def choose_filter(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    filter_type = callback.data.split(":")[-1]

    if filter_type == "all":
        await state.update_data(filter_type="all")
        await state.set_state(AdminBroadcastStates.waiting_for_content)
        await callback.message.edit_text(
            "👥 <b>Ба ҳама user’ҳо</b>\n\n"
            "<blockquote>Акнун тайёр хабар/фото/видео/голосро фиристед.</blockquote>"
        )

    elif filter_type == "status":
        await state.update_data(filter_type="status")
        await state.set_state(AdminBroadcastStates.choosing_status)
        await callback.message.edit_text(
            "📦 <b>Статусро интихоб кунед:</b>",
            reply_markup=broadcast_status_keyboard(),
        )

    elif filter_type == "date":
        await state.update_data(filter_type="date")
        await state.set_state(AdminBroadcastStates.choosing_date_field)
        await callback.message.edit_text(
            "📅 <b>Кадом санаро истифода мебарем?</b>",
            reply_markup=broadcast_date_field_keyboard(),
        )

    elif filter_type == "telegram_id":
        await state.update_data(filter_type="telegram_id")
        await state.set_state(AdminBroadcastStates.waiting_for_telegram_id)
        await callback.message.edit_text(
            "🆔 <b>Telegram ID ворид кунед:</b>"
        )

    elif filter_type == "track_code":
        await state.update_data(filter_type="track_code")
        await state.set_state(AdminBroadcastStates.waiting_for_track_code)
        await callback.message.edit_text(
            "🔢 <b>Трек-кодро ворид кунед:</b>\n\n"
            "<blockquote>Мисол: <code>SF123456789CN</code></blockquote>"
        )

    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:status:"))
async def choose_status(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    status_code = callback.data.split(":")[-1]
    await state.update_data(status_code=status_code)
    await state.set_state(AdminBroadcastStates.waiting_for_content)

    await callback.message.edit_text(
        f"📦 <b>{format_status(status_code, '', LANG_TJ)}</b>\n\n"
        "<blockquote>Акнун тайёр хабар/фото/видео/голосро фиристед.</blockquote>"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast:date_field:"))
async def choose_date_field(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    date_field = callback.data.split(":")[-1]
    await state.update_data(date_field=date_field)
    await state.set_state(AdminBroadcastStates.waiting_for_date)

    await callback.message.edit_text(
        "📅 <b>Санаро ворид кунед:</b>\n\n"
        "<blockquote>Формат: <code>DD.MM.YYYY</code>\n"
        "Мисол: <code>17.05.2026</code></blockquote>"
    )
    await callback.answer()


@router.message(AdminBroadcastStates.waiting_for_date)
async def receive_date(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        return

    parsed = _parse_date(message.text or "")
    if parsed is None:
        await message.answer(
            "❌ <b>Сана нодуруст аст.</b>\n\n"
            "Мисол: <code>17.05.2026</code>"
        )
        return

    await state.update_data(target_date=parsed.strftime("%d.%m.%Y"))
    await state.set_state(AdminBroadcastStates.waiting_for_content)

    await message.answer(
        "✅ <b>Сана қабул шуд.</b>\n\n"
        "<blockquote>Акнун тайёр хабар/фото/видео/голосро фиристед.</blockquote>"
    )


@router.message(AdminBroadcastStates.waiting_for_telegram_id)
async def receive_telegram_id(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        return

    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("❌ <b>Telegram ID фақат рақам бошад.</b>")
        return

    await state.update_data(telegram_id=int(raw))
    await state.set_state(AdminBroadcastStates.waiting_for_content)

    await message.answer(
        "✅ <b>Telegram ID қабул шуд.</b>\n\n"
        "<blockquote>Акнун тайёр хабар/фото/видео/голосро фиристед.</blockquote>"
    )



@router.message(AdminBroadcastStates.waiting_for_track_code)
async def receive_track_code(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        return

    raw = (message.text or "").strip()
    if not raw:
        await message.answer("❌ <b>Трек-код нодуруст аст.</b>")
        return

    normalized_track_code = normalize_track_code(raw)

    async with async_session() as session:
        result = await session.execute(
            select(Parcel, User)
            .join(User, Parcel.user_id == User.id)
            .where(Parcel.normalized_track_code == normalized_track_code)
        )
        row = result.first()

    if row is None:
        await message.answer(
            "❌ <b>Ин трек-код дар база ёфт нашуд.</b>"
        )
        return

    parcel, user = row

    if not user.telegram_id:
        await message.answer(
            "❌ <b>Ин user Telegram ID надорад.</b>\n\n"
            "<blockquote>Эҳтимол user ҳоло ботро истифода накардааст.</blockquote>"
        )
        return

    await state.update_data(
        track_code=parcel.track_code,
        telegram_id=user.telegram_id,
    )
    await state.set_state(AdminBroadcastStates.waiting_for_content)

    await message.answer(
        "✅ <b>Трек-код қабул шуд.</b>\n\n"
        f"<blockquote>"
        f"Трек-код: <code>{parcel.track_code}</code>\n"
        f"Мизоҷ: <b>{user.full_name}</b>\n"
        f"Telegram ID: <code>{user.telegram_id}</code>"
        f"</blockquote>\n\n"
        "Акнун тайёр хабар/фото/видео/голосро фиристед."
    )


@router.message(AdminBroadcastStates.waiting_for_content)
async def receive_broadcast_content(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not is_admin(message.from_user.id):
        return

    ok = await _save_content(message, state)
    if not ok:
        await message.answer(
            "❌ <b>Ин навъи хабар ҳоло дастгирӣ намешавад.</b>\n\n"
            "<blockquote>Матн, фото, видео ё голос фиристед.</blockquote>"
        )
        return

    data = await state.get_data()
    recipients = await _target_telegram_ids(data)
    await state.update_data(recipients=recipients)
    await state.set_state(AdminBroadcastStates.confirming)

    content = (await state.get_data()).get("content", {})
    await _preview_content(message, content)

    await message.answer(
        "📣 <b>Паёми гурӯҳӣ</b>\n\n"
        f"<blockquote>"
        f"Филтр: <b>{_filter_title(data)}</b>\n"
        f"Қабулкунандаҳо: <b>{len(recipients)}</b>"
        f"</blockquote>\n\n"
        "Фиристода шавад?",
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.callback_query(F.data == "broadcast:send")
async def send_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not is_admin(callback.from_user.id):
        await callback.answer()
        return

    data = await state.get_data()
    recipients = data.get("recipients", [])
    content = data.get("content")

    if not content:
        await callback.message.answer("❌ Хабар ёфт нашуд.")
        await state.clear()
        await callback.answer()
        return

    success = 0
    failed = 0

    for chat_id in recipients:
        try:
            await _send_content(callback.bot, int(chat_id), content)
            success += 1
        except Exception:
            failed += 1

    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Паёми гурӯҳӣ фиристода шуд</b>\n\n"
        f"<blockquote>"
        f"Юборида шуд: <b>{success}</b>\n"
        f"Хато: <b>{failed}</b>"
        f"</blockquote>"
    )
    await callback.answer()
