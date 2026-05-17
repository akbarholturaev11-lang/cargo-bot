from services.settings import get_many_settings
from utils.constants import (
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
    STATUS_ARRIVED_DESTINATION,
    STATUS_RECEIVED,
)

STATUS_IMAGE_KEYS = {
    STATUS_CHINA_RECEIVED: "status_image_china_received_file_id",
    STATUS_ON_THE_WAY: "status_image_on_the_way_file_id",
    STATUS_ARRIVED_DESTINATION: "status_image_arrived_destination_file_id",
    STATUS_RECEIVED: "status_image_received_file_id",
}


async def get_status_image_file_id(status_code: str | None) -> str:
    key = STATUS_IMAGE_KEYS.get(status_code or "")

    defaults = {
        "status_image_file_id": "",
    }

    if key:
        defaults[key] = ""

    values = await get_many_settings(defaults)

    if key:
        specific = (values.get(key) or "").strip()
        if specific:
            return specific

    return (values.get("status_image_file_id") or "").strip()
