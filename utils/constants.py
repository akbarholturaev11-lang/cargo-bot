LANG_TJ = "tj"
LANG_RU = "ru"
LANGUAGE_CODES = (LANG_TJ, LANG_RU)

STATUS_CHINA_RECEIVED = "china_received"
STATUS_ON_THE_WAY = "on_the_way"
STATUS_ARRIVED_DESTINATION = "arrived_destination"
STATUS_RECEIVED = "received"
STATUS_CODES = (
    STATUS_CHINA_RECEIVED,
    STATUS_ON_THE_WAY,
    STATUS_ARRIVED_DESTINATION,
    STATUS_RECEIVED,
)

DELIVERY_STATUS_NEW = "new"
DELIVERY_STATUS_ACCEPTED = "accepted"
DELIVERY_STATUS_ON_DELIVERY = "on_delivery"
DELIVERY_STATUS_DELIVERED = "delivered"
DELIVERY_STATUS_CANCELLED = "cancelled"
DELIVERY_STATUSES = (
    DELIVERY_STATUS_NEW,
    DELIVERY_STATUS_ACCEPTED,
    DELIVERY_STATUS_ON_DELIVERY,
    DELIVERY_STATUS_DELIVERED,
    DELIVERY_STATUS_CANCELLED,
)

CITY_ISTARAVSHAN = "istaravshan"
CITY_DUSHANBE = "dushanbe"
CITY_KHUJAND = "khujand"
CITY_BOKHTAR = "bokhtar"
CITY_KULOB = "kulob"
CITY_KEYS = (
    CITY_ISTARAVSHAN,
    CITY_DUSHANBE,
    CITY_KHUJAND,
    CITY_BOKHTAR,
    CITY_KULOB,
)

CITY_NAMES = {
    CITY_ISTARAVSHAN: {
        LANG_TJ: "Истаравшан",
        LANG_RU: "Истаравшан",
    },
    CITY_DUSHANBE: {
        LANG_TJ: "Душанбе",
        LANG_RU: "Душанбе",
    },
    CITY_KHUJAND: {
        LANG_TJ: "Хуҷанд",
        LANG_RU: "Худжанд",
    },
    CITY_BOKHTAR: {
        LANG_TJ: "Бохтар",
        LANG_RU: "Бохтар",
    },
    CITY_KULOB: {
        LANG_TJ: "Кӯлоб",
        LANG_RU: "Куляб",
    },
}
