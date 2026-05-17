from utils.constants import (
    LANG_RU,
    LANG_TJ,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
    STATUS_RECEIVED,
)


STATUS_TEXTS = {
    LANG_TJ: {
        STATUS_CHINA_RECEIVED: "🇨🇳 Дар склади Чин",
        STATUS_ON_THE_WAY: "🚚 Дар роҳ",
        STATUS_ARRIVED_DESTINATION: "🏬 Ба склад расид",
    },
    LANG_RU: {
        STATUS_CHINA_RECEIVED: "🇨🇳 На складе в Китае",
        STATUS_ON_THE_WAY: "🚚 В пути",
        STATUS_ARRIVED_DESTINATION: "🏬 Прибыл на склад",
    },
}


def format_status(status_code: str, city: str, lang: str) -> str:
    texts = STATUS_TEXTS.get(lang, STATUS_TEXTS[LANG_TJ])
    template = texts.get(status_code, status_code)
    return template.format(city=city)
