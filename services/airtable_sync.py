from __future__ import annotations

from datetime import date
import logging
import os
from typing import Any


logger = logging.getLogger(__name__)

AIRTABLE_ENABLED = os.getenv("AIRTABLE_ENABLED", "false").strip().lower() == "true"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")

TABLE_USERS = "Истифодабарандагон"
TABLE_PARCELS = "Борҳо"
TABLE_WAREHOUSES = "Складҳо"
TABLE_DELIVERY_REQUESTS = "Дархостҳои доставка"
TABLE_SETTINGS = "Танзимот"
TABLE_DAILY_STATS = "Статистикаи рӯзона"

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


def _is_configured() -> bool:
    return AIRTABLE_ENABLED and bool(AIRTABLE_API_KEY and AIRTABLE_BASE_ID)


async def _safe_sync(table_name: str, payload: dict[str, Any]) -> bool:
    if not _is_configured():
        logger.debug("Airtable sync skipped for %s: not configured", table_name)
        return False

    try:
        # Future implementation:
        # 1. Read the source record from PostgreSQL.
        # 2. Map fields to the Tajik Airtable table schema.
        # 3. Upsert into Airtable using AIRTABLE_BASE_ID.
        #
        # Airtable must never be used as the bot's source of truth.
        logger.info("Airtable sync placeholder for %s: %s", table_name, payload)
        return True
    except Exception:
        logger.exception("Airtable sync failed for %s", table_name)
        return False


async def sync_user_to_airtable(user_id: int) -> bool:
    return await _safe_sync(TABLE_USERS, {"user_id": user_id})


async def sync_parcel_to_airtable(parcel_id: int) -> bool:
    return await _safe_sync(TABLE_PARCELS, {"parcel_id": parcel_id})


async def sync_delivery_request_to_airtable(request_id: int) -> bool:
    return await _safe_sync(TABLE_DELIVERY_REQUESTS, {"request_id": request_id})


async def sync_daily_stats_to_airtable(stats_date: date) -> bool:
    return await _safe_sync(
        TABLE_DAILY_STATS,
        {"date": stats_date.isoformat()},
    )
