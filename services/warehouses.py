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


def city_key_from_name(city_name: str) -> str | None:
    normalized_city = city_name.strip().casefold()
    for city_key, names in CITY_NAMES.items():
        if normalized_city == city_key.casefold():
            return city_key
        if any(normalized_city == name.casefold() for name in names.values()):
            return city_key
    return None


async def get_warehouse_by_id(warehouse_id: int) -> Warehouse | None:
    async with async_session() as session:
        return await session.get(Warehouse, warehouse_id)


async def get_active_warehouse_by_city_name(city_name: str) -> Warehouse | None:
    city_key = city_key_from_name(city_name)
    if city_key is None:
        return None
    return await get_active_warehouse(city_key)


async def get_warehouse_for_parcel_destination(
    *,
    destination_warehouse_id: int | None,
    destination_city: str,
) -> Warehouse | None:
    if destination_warehouse_id is not None:
        warehouse = await get_warehouse_by_id(destination_warehouse_id)
        if warehouse is not None:
            return warehouse

    return await get_active_warehouse_by_city_name(destination_city)


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


async def get_active_warehouses() -> list[Warehouse]:
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse)
            .where(Warehouse.is_active.is_(True))
            .order_by(Warehouse.city_key, Warehouse.updated_at.desc(), Warehouse.id.desc())
        )
        warehouses = list(result.scalars().all())

    # User side must show only warehouses that already have an address/media block.
    # If admin creates a warehouse without address/caption/media, it stays hidden.
    visible_warehouses = []
    for warehouse in warehouses:
        has_caption = bool((warehouse.address_caption or "").strip())
        has_media = bool((warehouse.media_file_id or "").strip())
        if has_caption or has_media:
            visible_warehouses.append(warehouse)

    return visible_warehouses


async def get_user_warehouse(user_city: str | None) -> tuple[Warehouse | None, str]:
    active_warehouses = await get_active_warehouses()

    if not active_warehouses:
        return None, "no_warehouses"

    if len(active_warehouses) == 1:
        return active_warehouses[0], "single"

    if user_city:
        normalized_city = str(user_city).strip().lower()

        for warehouse in active_warehouses:
            values = {
                str(warehouse.city_key).strip().lower(),
                str(warehouse.city_name_tj).strip().lower(),
                str(warehouse.city_name_ru).strip().lower(),
            }

            if normalized_city in values:
                return warehouse, "user_city"

    return None, "need_choose"


async def save_tj_pickup_warehouse(
    *,
    city_key: str,
    media_type: str,
    media_file_id: str | None,
    caption: str,
) -> Warehouse | None:
    if media_type not in {"photo", "video", "text"}:
        media_type = "text"
        media_file_id = None

    async with async_session() as session:
        result = await session.execute(
            select(Warehouse)
            .where(Warehouse.city_key == city_key)
            .order_by(Warehouse.updated_at.desc(), Warehouse.id.desc())
            .limit(1)
        )
        warehouse = result.scalar_one_or_none()

        if warehouse is None:
            city_names = CITY_NAMES[city_key]
            warehouse = Warehouse(
                city_key=city_key,
                city_name_tj=city_names[LANG_TJ],
                city_name_ru=city_names[LANG_RU],
                address_caption="",
                image_file_id=None,
                media_type="text",
                media_file_id=None,
                is_active=True,
            )
            session.add(warehouse)

        warehouse.tj_pickup_caption = caption
        warehouse.tj_pickup_media_type = media_type
        warehouse.tj_pickup_media_file_id = media_file_id
        warehouse.is_active = True

        await session.commit()
        await session.refresh(warehouse)
        return warehouse


def warehouse_has_tj_pickup_block(warehouse: Warehouse | None) -> bool:
    if warehouse is None:
        return False

    has_caption = bool((warehouse.tj_pickup_caption or "").strip())
    has_media = bool((warehouse.tj_pickup_media_file_id or "").strip())

    return has_caption or has_media


async def get_active_tj_pickup_warehouses() -> list[Warehouse]:
    async with async_session() as session:
        result = await session.execute(
            select(Warehouse)
            .where(Warehouse.is_active.is_(True))
            .order_by(Warehouse.city_name_tj.asc())
        )
        warehouses = list(result.scalars().all())

    return [
        warehouse for warehouse in warehouses
        if warehouse_has_tj_pickup_block(warehouse)
    ]
