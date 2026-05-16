from decimal import Decimal, InvalidOperation


def parse_positive_decimal(value: str) -> Decimal | None:
    normalized = value.strip().replace(",", ".")
    try:
        number = Decimal(normalized)
    except InvalidOperation:
        return None

    if number <= 0:
        return None
    return number


def format_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


async def get_price_per_kg() -> Decimal:
    from services.settings import get_setting

    value = await get_setting("price_per_kg_tjs", "25")
    try:
        return Decimal(value or "25")
    except InvalidOperation:
        return Decimal("25")


async def get_price_per_cube() -> Decimal:
    from services.settings import get_setting

    value = await get_setting("price_per_cube_tjs", "3500")
    try:
        return Decimal(value or "3500")
    except InvalidOperation:
        return Decimal("3500")


def calculate_total(amount: Decimal, price: Decimal) -> Decimal:
    return amount * price
