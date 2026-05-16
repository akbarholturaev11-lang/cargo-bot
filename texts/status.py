from utils.constants import (
    LANG_RU,
    LANG_TJ,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
)


STATUS_TEXTS = {
    LANG_TJ: {
        STATUS_CHINA_RECEIVED: "Дар склади Чин қабул шуд",
        STATUS_ON_THE_WAY: "Дар роҳ аст",
        STATUS_ARRIVED_DESTINATION: "Ба склади {city} расид — омода барои гирифтан",
    },
    LANG_RU: {
        STATUS_CHINA_RECEIVED: "Принят на складе в Китае",
        STATUS_ON_THE_WAY: "В пути",
        STATUS_ARRIVED_DESTINATION: "Прибыл на склад {city} — готов к получению",
    },
}


def format_status(status_code: str, city: str, lang: str) -> str:
    texts = STATUS_TEXTS.get(lang, STATUS_TEXTS[LANG_TJ])
    template = texts.get(status_code, status_code)
    return template.format(city=city)
