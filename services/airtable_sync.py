from __future__ import annotations

import asyncio
from collections.abc import Iterable, Sequence
from datetime import date, datetime
import json
import logging
import os
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from database.db import async_session
from database.models import DeliveryRequest, Parcel, User, Warehouse
from utils.constants import (
    DELIVERY_STATUS_NEW,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
    STATUS_RECEIVED,
)


logger = logging.getLogger(__name__)

AIRTABLE_ENABLED = os.getenv("AIRTABLE_ENABLED", "false").strip().lower() == "true"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_API_URL = os.getenv("AIRTABLE_API_URL", "https://api.airtable.com/v0").rstrip("/")
AIRTABLE_TIMEOUT_SECONDS = float(os.getenv("AIRTABLE_TIMEOUT_SECONDS", "10"))
AIRTABLE_SYNC_KEY_FIELD = os.getenv("AIRTABLE_SYNC_KEY_FIELD", "Source ID").strip()
AIRTABLE_PRIMARY_FIELD = os.getenv("AIRTABLE_PRIMARY_FIELD", "Name").strip()

TABLE_USERS = os.getenv("AIRTABLE_USERS_TABLE", "Истифодабарандагон")
TABLE_PARCELS = os.getenv("AIRTABLE_PARCELS_TABLE", "Борҳо")
TABLE_WAREHOUSES = os.getenv("AIRTABLE_WAREHOUSES_TABLE", "Складҳо")
TABLE_DELIVERY_REQUESTS = os.getenv(
    "AIRTABLE_DELIVERY_TABLE",
    os.getenv("AIRTABLE_DELIVERY_REQUESTS_TABLE", "Дархостҳои доставка"),
)
TABLE_SETTINGS = os.getenv("AIRTABLE_SETTINGS_TABLE", "Танзимот")
TABLE_DAILY_STATS = os.getenv("AIRTABLE_DAILY_STATS_TABLE", "Статистикаи рӯзона")

AIRTABLE_BATCH_SIZE = 10
AIRTABLE_MIN_REQUEST_INTERVAL_SECONDS = 0.22

AIRTABLE_TABLES = {
    "users": TABLE_USERS,
    "parcels": TABLE_PARCELS,
    "warehouses": TABLE_WAREHOUSES,
    "delivery_requests": TABLE_DELIVERY_REQUESTS,
    "settings": TABLE_SETTINGS,
    "daily_stats": TABLE_DAILY_STATS,
}

AIRTABLE_VIEWS = {
    TABLE_PARCELS: (
        "Ҳамаи борҳо",
        "Дар склади Чин",
        "Дар роҳ",
        "Ба склад расида",
        "Имрӯз қабулшуда",
        "Мушкилдор",
    ),
    TABLE_USERS: (
        "Ҳамаи мизоҷон",
        "Мизоҷони фаъол",
        "Мизоҷони нав",
    ),
    TABLE_DELIVERY_REQUESTS: (
        "Дархостҳои нав",
        "Қабулшуда",
        "Дар роҳ",
        "Расонида шуд",
        "Бекоршуда",
    ),
}


class AirtableSyncError(RuntimeError):
    pass


def _is_configured() -> bool:
    return AIRTABLE_ENABLED and bool(
        AIRTABLE_API_KEY
        and AIRTABLE_BASE_ID
        and AIRTABLE_SYNC_KEY_FIELD
    )


def _to_airtable_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bool | int | float | str):
        return value
    if value is None:
        return None
    return str(value)


def _compact_fields(fields: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _to_airtable_value(value)
        for key, value in fields.items()
        if value is not None
    }


def _base_fields(source_id: str, name: str) -> dict[str, Any]:
    fields = {AIRTABLE_SYNC_KEY_FIELD: source_id}
    if AIRTABLE_PRIMARY_FIELD:
        fields[AIRTABLE_PRIMARY_FIELD] = name
    return fields


def _chunks(items: Sequence[dict[str, Any]], size: int) -> Iterable[Sequence[dict[str, Any]]]:
    for index in range(0, len(items), size):
        yield items[index:index + size]


def _request_airtable(
    *,
    method: str,
    table_name: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    table_path = quote(table_name, safe="")
    base_path = quote(AIRTABLE_BASE_ID, safe="")
    url = f"{AIRTABLE_API_URL}/{base_path}/{table_path}"
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=AIRTABLE_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise AirtableSyncError(f"Airtable API error {error.code}: {body}") from error
    except URLError as error:
        raise AirtableSyncError(f"Airtable connection error: {error.reason}") from error

    if not body:
        return {}
    return json.loads(body)


async def _upsert_records(
    *,
    table_name: str,
    records: Sequence[dict[str, Any]],
) -> None:
    for batch in _chunks(records, AIRTABLE_BATCH_SIZE):
        payload = {
            "performUpsert": {
                "fieldsToMergeOn": [AIRTABLE_SYNC_KEY_FIELD],
            },
            "records": [{"fields": fields} for fields in batch],
            "typecast": True,
        }
        await asyncio.to_thread(
            _request_airtable,
            method="PATCH",
            table_name=table_name,
            payload=payload,
        )

        if len(records) > AIRTABLE_BATCH_SIZE:
            await asyncio.to_thread(sleep, AIRTABLE_MIN_REQUEST_INTERVAL_SECONDS)


async def _safe_upsert(
    *,
    table_name: str,
    records: Sequence[dict[str, Any]],
    label: str,
) -> bool:
    if not _is_configured():
        logger.debug("Airtable sync skipped for %s: not configured", label)
        return False

    if not records:
        return True

    try:
        await _upsert_records(table_name=table_name, records=records)
        return True
    except Exception:
        logger.exception("Airtable sync failed for %s", label)
        return False


def _user_fields(user: User) -> dict[str, Any]:
    return _compact_fields(
        {
            **_base_fields(f"user:{user.id}", f"{user.client_code} - {user.full_name}"),
            "User ID": user.id,
            "Telegram ID": user.telegram_id,
            "Username": user.username,
            "Language": user.language,
            "Full Name": user.full_name,
            "Phone": user.phone,
            "City": user.city,
            "Client Code": user.client_code,
            "Status": user.status,
            "Created At": user.created_at,
            "Last Seen": user.last_seen,
        },
    )


def _parcel_fields(parcel: Parcel) -> dict[str, Any]:
    user = getattr(parcel, "user", None)
    return _compact_fields(
        {
            **_base_fields(f"parcel:{parcel.id}", parcel.track_code),
            "Parcel ID": parcel.id,
            "Track Code": parcel.track_code,
            "Normalized Track Code": parcel.normalized_track_code,
            "Client Code": parcel.client_code,
            "User ID": parcel.user_id,
            "User Full Name": getattr(user, "full_name", None),
            "User Phone": getattr(user, "phone", None),
            "Destination City": parcel.destination_city,
            "Destination Warehouse ID": parcel.destination_warehouse_id,
            "Status": parcel.status_code,
            "Received China At": parcel.received_china_at,
            "Batch Date": parcel.batch_date,
            "China Received Notified At": parcel.china_received_notified_at,
            "Arrival Notified At": parcel.arrival_notified_at,
            "Created By Admin ID": parcel.created_by_admin_id,
            "Created At": parcel.created_at,
            "Updated At": parcel.updated_at,
        },
    )


def _warehouse_fields(warehouse: Warehouse) -> dict[str, Any]:
    return _compact_fields(
        {
            **_base_fields(
                f"warehouse:{warehouse.id}",
                f"{warehouse.city_name_tj} / {warehouse.city_name_ru}",
            ),
            "Warehouse ID": warehouse.id,
            "City Key": warehouse.city_key,
            "City Name TJ": warehouse.city_name_tj,
            "City Name RU": warehouse.city_name_ru,
            "Address Caption": warehouse.address_caption,
            "Image File ID": warehouse.image_file_id,
            "Media Type": warehouse.media_type,
            "Media File ID": warehouse.media_file_id,
            "TJ Address Text": warehouse.tj_address_text,
            "TJ Work Time": warehouse.tj_work_time,
            "TJ Phone": warehouse.tj_phone,
            "TJ Pickup Caption": warehouse.tj_pickup_caption,
            "TJ Pickup Media Type": warehouse.tj_pickup_media_type,
            "TJ Pickup Media File ID": warehouse.tj_pickup_media_file_id,
            "Active": warehouse.is_active,
            "Created At": warehouse.created_at,
            "Updated At": warehouse.updated_at,
        },
    )


def _delivery_request_fields(request: DeliveryRequest) -> dict[str, Any]:
    user = getattr(request, "user", None)
    return _compact_fields(
        {
            **_base_fields(f"delivery:{request.id}", f"{request.track_code} delivery"),
            "Delivery Request ID": request.id,
            "Parcel ID": request.parcel_id,
            "User ID": request.user_id,
            "User Full Name": getattr(user, "full_name", None),
            "Client Code": getattr(user, "client_code", None),
            "Track Code": request.track_code,
            "Destination City": request.destination_city,
            "Delivery Address": request.delivery_address,
            "Delivery Phone": request.delivery_phone,
            "Status": request.status,
            "Handled By Admin ID": request.handled_by_admin_id,
            "Created At": request.created_at,
            "Updated At": request.updated_at,
        },
    )


async def sync_user_to_airtable(user_id: int) -> bool:
    if not _is_configured():
        logger.debug("Airtable sync skipped for user:%s: not configured", user_id)
        return False

    try:
        async with async_session() as session:
            user = await session.get(User, user_id)
            if user is None:
                return False

        return await _safe_upsert(
            table_name=TABLE_USERS,
            records=[_user_fields(user)],
            label=f"user:{user_id}",
        )
    except Exception:
        logger.exception("Airtable sync failed for user:%s", user_id)
        return False


async def sync_parcel_to_airtable(parcel_id: int) -> bool:
    return await sync_parcels_to_airtable([parcel_id])


async def sync_parcels_to_airtable(parcel_ids: Sequence[int]) -> bool:
    if not _is_configured():
        logger.debug("Airtable sync skipped for parcels: not configured")
        return False

    if not parcel_ids:
        return True

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Parcel)
                .options(selectinload(Parcel.user))
                .where(Parcel.id.in_(parcel_ids)),
            )
            parcels = list(result.scalars().all())

        return await _safe_upsert(
            table_name=TABLE_PARCELS,
            records=[_parcel_fields(parcel) for parcel in parcels],
            label=f"parcels:{','.join(str(parcel_id) for parcel_id in parcel_ids)}",
        )
    except Exception:
        logger.exception("Airtable sync failed for parcels")
        return False


async def sync_warehouse_to_airtable(warehouse_id: int) -> bool:
    if not _is_configured():
        logger.debug("Airtable sync skipped for warehouse:%s: not configured", warehouse_id)
        return False

    try:
        async with async_session() as session:
            warehouse = await session.get(Warehouse, warehouse_id)
            if warehouse is None:
                return False

        return await _safe_upsert(
            table_name=TABLE_WAREHOUSES,
            records=[_warehouse_fields(warehouse)],
            label=f"warehouse:{warehouse_id}",
        )
    except Exception:
        logger.exception("Airtable sync failed for warehouse:%s", warehouse_id)
        return False


async def sync_delivery_request_to_airtable(request_id: int) -> bool:
    if not _is_configured():
        logger.debug("Airtable sync skipped for delivery:%s: not configured", request_id)
        return False

    try:
        async with async_session() as session:
            result = await session.execute(
                select(DeliveryRequest)
                .options(
                    selectinload(DeliveryRequest.user),
                    selectinload(DeliveryRequest.parcel),
                )
                .where(DeliveryRequest.id == request_id),
            )
            request = result.scalar_one_or_none()
            if request is None:
                return False

        return await _safe_upsert(
            table_name=TABLE_DELIVERY_REQUESTS,
            records=[_delivery_request_fields(request)],
            label=f"delivery:{request_id}",
        )
    except Exception:
        logger.exception("Airtable sync failed for delivery:%s", request_id)
        return False


async def _count(session, statement) -> int:
    result = await session.execute(statement)
    return int(result.scalar_one() or 0)


async def sync_daily_stats_to_airtable(stats_date: date) -> bool:
    if not _is_configured():
        logger.debug(
            "Airtable sync skipped for daily_stats:%s: not configured",
            stats_date.isoformat(),
        )
        return False

    try:
        async with async_session() as session:
            date_filter = func.date
            fields = _compact_fields(
                {
                    **_base_fields(
                        f"daily_stats:{stats_date.isoformat()}",
                        f"Stats {stats_date.isoformat()}",
                    ),
                    "Date": stats_date,
                    "Total Users": await _count(session, select(func.count(User.id))),
                    "New Users": await _count(
                        session,
                        select(func.count(User.id)).where(
                            date_filter(User.created_at) == stats_date,
                        ),
                    ),
                    "Total Parcels": await _count(session, select(func.count(Parcel.id))),
                    "New Parcels": await _count(
                        session,
                        select(func.count(Parcel.id)).where(
                            date_filter(Parcel.created_at) == stats_date,
                        ),
                    ),
                    "Parcels Received China": await _count(
                        session,
                        select(func.count(Parcel.id)).where(Parcel.batch_date == stats_date),
                    ),
                    "Delivery Requests": await _count(
                        session,
                        select(func.count(DeliveryRequest.id)).where(
                            date_filter(DeliveryRequest.created_at) == stats_date,
                        ),
                    ),
                    "New Delivery Requests": await _count(
                        session,
                        select(func.count(DeliveryRequest.id)).where(
                            DeliveryRequest.status == DELIVERY_STATUS_NEW,
                        ),
                    ),
                    "China Received Parcels": await _count(
                        session,
                        select(func.count(Parcel.id)).where(
                            Parcel.status_code == STATUS_CHINA_RECEIVED,
                        ),
                    ),
                    "On The Way Parcels": await _count(
                        session,
                        select(func.count(Parcel.id)).where(
                            Parcel.status_code == STATUS_ON_THE_WAY,
                        ),
                    ),
                    "Arrived Parcels": await _count(
                        session,
                        select(func.count(Parcel.id)).where(
                            Parcel.status_code == STATUS_ARRIVED_DESTINATION,
                        ),
                    ),
                    "Received Parcels": await _count(
                        session,
                        select(func.count(Parcel.id)).where(
                            Parcel.status_code == STATUS_RECEIVED,
                        ),
                    ),
                },
            )

        return await _safe_upsert(
            table_name=TABLE_DAILY_STATS,
            records=[fields],
            label=f"daily_stats:{stats_date.isoformat()}",
        )
    except Exception:
        logger.exception(
            "Airtable sync failed for daily_stats:%s",
            stats_date.isoformat(),
        )
        return False
