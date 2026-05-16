import re


def normalize_track_code(track_code: str) -> str:
    without_spaces = re.sub(r"\s+", "", track_code)
    return without_spaces.replace("-", "").upper()


def normalize_full_name(full_name: str) -> str:
    normalized = full_name.strip().lower()
    return re.sub(r"\s+", " ", normalized)
