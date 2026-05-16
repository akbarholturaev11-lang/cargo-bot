from sqlalchemy import select

from database.db import async_session
from database.models import Warehouse
from utils.constants import CITY_NAMES, LANG_RU, LANG_TJ


async def get_active_warehouse(city_key: str) -> Warehouse | None:
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse)
            .where(
                Warehouse.city_key == city_key,
                Warehouse.is_active.is_(True),
            )
            .order_by(Warehouse.updated_at.desc(), Warehouse.id.desc())
            .limit(1),
        )
        return result.scalar_one_or_none()


async def get_warehouse_by_city_key(city_key: str) -> Warehouse | None:
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse)
            .where(Warehouse.city_key == city_key)
            .order_by(Warehouse.updated_at.desc(), Warehouse.id.desc())
            .limit(1),
        )
        return result.scalar_one_or_none()


async def list_warehouses() -> list[Warehouse]:
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse).order_by(Warehouse.city_key, Warehouse.id),
        )
        return list(result.scalars().all())


async def save_active_warehouse(
    *,
    city_key: str,
    media_type: str,
    media_file_id: str | None,
    address_caption: str,
) -> Warehouse:
    if media_type not in {"photo", "video", "text"}:
        media_type = "text"
        media_file_id = None

    city_names = CITY_NAMES[city_key]
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse)
            .where(Warehouse.city_key == city_key)
            .order_by(Warehouse.updated_at.desc(), Warehouse.id.desc())
        )
        warehouses = list(result.scalars().all())
        warehouse = warehouses[0] if warehouses else None

        if warehouse is None:
            warehouse = Warehouse(
                city_key=city_key,
                city_name_tj=city_names[LANG_TJ],
                city_name_ru=city_names[LANG_RU],
                address_caption=address_caption,
                image_file_id=media_file_id if media_type == "photo" else None,
                media_type=media_type,
                media_file_id=media_file_id,
                is_active=True,
            )
            session.add(warehouse)
        else:
            warehouse.city_name_tj = city_names[LANG_TJ]
            warehouse.city_name_ru = city_names[LANG_RU]
            warehouse.address_caption = address_caption
            warehouse.image_file_id = media_file_id if media_type == "photo" else None
            warehouse.media_type = media_type
            warehouse.media_file_id = media_file_id
            warehouse.is_active = True

        for old_warehouse in warehouses[1:]:
            old_warehouse.is_active = False

        await session.commit()
        await session.refresh(warehouse)
        return warehouse


async def set_warehouse_inactive(city_key: str) -> int:
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse).where(Warehouse.city_key == city_key),
        )
        warehouses = list(result.scalars().all())

        for warehouse in warehouses:
            warehouse.is_active = False

        await session.commit()
        return len(warehouses)
