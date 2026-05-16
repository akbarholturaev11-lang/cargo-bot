from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Parcel, Setting, User, Warehouse


async def get_user_by_telegram_id(
    session: AsyncSession,
    telegram_id: int,
) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_phone(session: AsyncSession, phone: str) -> User | None:
    result = await session.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def get_user_by_client_code(
    session: AsyncSession,
    client_code: str,
) -> User | None:
    result = await session.execute(
        select(User).where(User.client_code == client_code),
    )
    return result.scalar_one_or_none()


async def get_last_client_code_with_prefix(
    session: AsyncSession,
    prefix: str,
) -> str | None:
    result = await session.execute(
        select(User.client_code)
        .where(User.client_code.like(f"{prefix}%"))
        .order_by(User.client_code.desc())
        .limit(1),
    )
    return result.scalar_one_or_none()


async def get_parcel_by_normalized_track_code(
    session: AsyncSession,
    normalized_track_code: str,
) -> Parcel | None:
    result = await session.execute(
        select(Parcel).where(Parcel.normalized_track_code == normalized_track_code),
    )
    return result.scalar_one_or_none()


async def get_active_warehouse_by_city_key(
    session: AsyncSession,
    city_key: str,
) -> Warehouse | None:
    result = await session.execute(
        select(Warehouse).where(
            Warehouse.city_key == city_key,
            Warehouse.is_active.is_(True),
        ),
    )
    return result.scalar_one_or_none()


async def get_setting(session: AsyncSession, key: str) -> Setting | None:
    result = await session.execute(select(Setting).where(Setting.key == key))
    return result.scalar_one_or_none()


async def set_setting(session: AsyncSession, key: str, value: str) -> Setting:
    setting = await get_setting(session, key)
    if setting is None:
        setting = Setting(key=key, value=value)
        session.add(setting)
    else:
        setting.value = value
    return setting
