from datetime import datetime, timezone
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import CLIENT_CODE_PREFIX
from database.db import async_session
from database.models import Setting, User
from services.normalizer import normalize_full_name
from utils.constants import CITY_NAMES, LANG_TJ


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone.strip())
    if len(digits) >= 9:
        return digits[-9:]
    return digits


def normalize_contact_phone(phone: str) -> str | None:
    digits = re.sub(r"\D", "", phone.strip())
    if len(digits) < 9:
        return None
    return digits[-9:]


def normalize_manual_phone(phone: str) -> str | None:
    value = phone.strip()
    if re.fullmatch(r"\d{9}", value) is None:
        return None
    return value


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id),
        )
        return result.scalar_one_or_none()


async def get_user_by_phone(phone: str) -> User | None:
    normalized_phone = normalize_phone(phone)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.phone == normalized_phone),
        )
        return result.scalar_one_or_none()


async def get_user_by_client_code(client_code: str) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.client_code == client_code.strip().upper()),
        )
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: int) -> User | None:
    async with async_session() as session:
        return await session.get(User, user_id)


async def _get_client_code_prefix(session: AsyncSession) -> str:
    result = await session.execute(
        select(Setting.value).where(Setting.key == "client_code_prefix"),
    )
    prefix = result.scalar_one_or_none() or CLIENT_CODE_PREFIX or "AK"
    return prefix.strip() or "AK"


def _client_code_number(client_code: str, prefix: str) -> int | None:
    if not client_code.startswith(prefix):
        return None

    suffix = client_code.removeprefix(prefix)
    if not suffix.isdigit():
        return None
    return int(suffix)


async def generate_client_code(session: AsyncSession) -> str:
    prefix = await _get_client_code_prefix(session)
    result = await session.execute(
        select(User.client_code).where(User.client_code.like(f"{prefix}%")),
    )
    numbers = [
        number
        for code in result.scalars().all()
        if (number := _client_code_number(code, prefix)) is not None
    ]

    next_number = max(numbers, default=1000) + 1
    while True:
        client_code = f"{prefix}{next_number}"
        exists = await session.execute(
            select(User.id).where(User.client_code == client_code),
        )
        if exists.scalar_one_or_none() is None:
            return client_code
        next_number += 1


async def create_user(
    *,
    telegram_id: int,
    username: str | None,
    language: str,
    full_name: str,
    phone: str,
    city: str,
) -> User:
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            language=language,
            full_name=full_name.strip(),
            normalized_full_name=normalize_full_name(full_name),
            phone=normalize_phone(phone),
            city=city,
            client_code=await generate_client_code(session),
            last_seen=datetime.now(timezone.utc),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def attach_telegram_account(
    user_id: int,
    *,
    telegram_id: int,
    username: str | None,
) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        user.telegram_id = telegram_id
        user.username = username
        user.last_seen = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)
        return user


def city_display_name(city: str, lang: str) -> str:
    if city in CITY_NAMES:
        return CITY_NAMES[city].get(lang, CITY_NAMES[city][LANG_TJ])

    for names in CITY_NAMES.values():
        if city in names.values():
            return names.get(lang, names[LANG_TJ])

    return city


async def update_user_full_name(user_id: int, full_name: str) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        user.full_name = full_name.strip()
        user.normalized_full_name = normalize_full_name(full_name)
        user.last_seen = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_phone(user_id: int, phone: str) -> User | None:
    normalized_phone = normalize_phone(phone)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.phone == normalized_phone,
                User.id != user_id,
            ),
        )
        if result.scalar_one_or_none() is not None:
            return None

        user = await session.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        user.phone = normalized_phone
        user.last_seen = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_city(user_id: int, city: str) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        user.city = city
        user.last_seen = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_language(user_id: int, language: str) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is None:
            raise ValueError("User not found")

        user.language = language
        user.last_seen = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(user)
        return user
