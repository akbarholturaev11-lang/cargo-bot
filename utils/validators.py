from config import ADMIN_IDS


def is_admin(telegram_id: int | None) -> bool:
    if telegram_id is None:
        return False
    return telegram_id in ADMIN_IDS
