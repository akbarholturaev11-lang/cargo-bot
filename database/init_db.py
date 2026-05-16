from sqlalchemy import text

from database.db import engine
from database.models import Base


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("ALTER TABLE warehouses ADD COLUMN IF NOT EXISTS media_type VARCHAR(16) DEFAULT 'photo'"),
        )
        await conn.execute(
            text("ALTER TABLE warehouses ADD COLUMN IF NOT EXISTS media_file_id VARCHAR(255)"),
        )
        await conn.execute(
            text("ALTER TABLE warehouses ALTER COLUMN image_file_id DROP NOT NULL"),
        )
        await conn.execute(
            text(
                "UPDATE warehouses "
                "SET media_type = 'photo', media_file_id = image_file_id "
                "WHERE media_file_id IS NULL AND image_file_id IS NOT NULL",
            ),
        )
