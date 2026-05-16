from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config import ADMIN_IDS
from database.db import async_session
from database.models import DeliveryRequest, Parcel, User
from services.normalizer import normalize_track_code
from utils.constants import (
    DELIVERY_STATUS_NEW,
    DELIVERY_STATUSES,
    STATUS_ARRIVED_DESTINATION,
)


async def get_arrived_parcel_for_user_by_track_code(
    *,
    user_id: int,
    track_code: str,
) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(
                Parcel.user_id == user_id,
                Parcel.normalized_track_code == normalize_track_code(track_code),
                Parcel.status_code == STATUS_ARRIVED_DESTINATION,
            ),
        )
        return result.scalar_one_or_none()


async def get_arrived_parcel_for_user_by_id(
    *,
    user_id: int,
    parcel_id: int,
) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(
                Parcel.id == parcel_id,
                Parcel.user_id == user_id,
                Parcel.status_code == STATUS_ARRIVED_DESTINATION,
            ),
        )
        return result.scalar_one_or_none()


async def get_latest_arrived_parcel_for_user(user_id: int) -> Parcel | None:
    async with async_session() as session:
        result = await session.execute(
            select(Parcel)
            .options(selectinload(Parcel.user))
            .where(
                Parcel.user_id == user_id,
                Parcel.status_code == STATUS_ARRIVED_DESTINATION,
            )
            .order_by(Parcel.updated_at.desc(), Parcel.id.desc())
            .limit(1),
        )
        return result.scalar_one_or_none()


async def create_delivery_request(
    *,
    parcel: Parcel,
    user: User,
    delivery_address: str,
) -> DeliveryRequest:
    async with async_session() as session:
        request = DeliveryRequest(
            parcel_id=parcel.id,
            user_id=user.id,
            track_code=parcel.track_code,
            destination_city=parcel.destination_city,
            delivery_address=delivery_address.strip(),
            delivery_phone=user.phone,
            status=DELIVERY_STATUS_NEW,
        )
        session.add(request)
        await session.commit()
        await session.refresh(request)
        return request


async def get_delivery_requests() -> list[DeliveryRequest]:
    async with async_session() as session:
        result = await session.execute(
            select(DeliveryRequest)
            .options(
                selectinload(DeliveryRequest.user),
                selectinload(DeliveryRequest.parcel),
            )
            .order_by(DeliveryRequest.created_at.desc(), DeliveryRequest.id.desc())
            .limit(30),
        )
        return list(result.scalars().all())


async def get_delivery_request(request_id: int) -> DeliveryRequest | None:
    async with async_session() as session:
        result = await session.execute(
            select(DeliveryRequest)
            .options(
                selectinload(DeliveryRequest.user),
                selectinload(DeliveryRequest.parcel),
            )
            .where(DeliveryRequest.id == request_id),
        )
        return result.scalar_one_or_none()


async def update_delivery_status(
    *,
    request_id: int,
    status: str,
    admin_id: int,
) -> DeliveryRequest | None:
    if status not in DELIVERY_STATUSES:
        return None

    async with async_session() as session:
        request = await session.get(DeliveryRequest, request_id)
        if request is None:
            return None

        request.status = status
        request.handled_by_admin_id = admin_id
        await session.commit()
        await session.refresh(request)
        return request


def format_delivery_request_for_admin(request: DeliveryRequest, user: User) -> str:
    return (
        "Дархости доставка\n\n"
        f"ID: {request.id}\n"
        f"Трек-код: {request.track_code}\n"
        f"Ном: {user.full_name}\n"
        f"Телефон: {request.delivery_phone}\n"
        f"Склад: {request.destination_city}\n"
        f"Адрес: {request.delivery_address}\n"
        f"Статус: {request.status}"
    )


async def notify_admins_about_delivery_request(
    bot: Bot,
    request: DeliveryRequest,
    user: User,
) -> tuple[int, int]:
    text = format_delivery_request_for_admin(request, user)
    sent = 0
    failed = 0

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=text)
            sent += 1
        except TelegramAPIError:
            failed += 1

    return sent, failed
