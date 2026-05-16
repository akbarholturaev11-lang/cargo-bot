CHOOSE_LANGUAGE = "Забонро интихоб кунед:"

REGISTER = "Бақайдгирӣ"
LOGIN = "Ворид шудан"

ASK_FULL_NAME = "Ному насаби худро пурра ворид кунед."
ASK_PHONE = "Рақами телефонро бо тугмаи поён фиристед."
ASK_CITY = "Шаҳри худро интихоб кунед."

REGISTRATION_COMPLETED = (
    "Бақайдгирӣ анҷом ёфт.\n"
    "Рамзи муштарии шумо: {client_code}"
)
LOGIN_SUCCESS = "Шумо ба ҳисоб ворид шудед."
PHONE_NOT_FOUND = "Ин рақами телефон дар база ёфт нашуд."
NAME_MISMATCH = "Ному насаб бо рақами телефон мувофиқат накард."

MENU_SEARCH_PARCEL = "Ҷустуҷӯи бор"
MENU_MY_PARCELS = "Борҳои ман"
MENU_CALCULATOR = "Ҳисоби тахминӣ"
MENU_PROFILE = "Профили ман"
MENU_WAREHOUSES = "Суроғаҳои склад"
MENU_PRICES = "Нархҳо"
MENU_OPERATOR = "Оператор"

PARCEL_FOUND = (
    "Бори шумо ёфт шуд\n\n"
    "Трек-код: {track_code}\n"
    "Статус: {dynamic_status}\n"
    "Склад: {destination_city}\n"
    "Санаи қабул дар склади Чин: {received_china_at}\n"
    "Муддати тахминии расидан: {delivery_days}\n\n"
    "Вазн ва маблағ баъди расидан маълум мешавад."
)
ASK_TRACK_CODE = "Трек-коди борро фиристед."
PARCEL_NOT_FOUND = "Ин трек-код ёфт нашуд."

MY_PARCELS_EMPTY = "Ҳоло барои шумо бор сабт нашудааст."
MY_PARCELS_TITLE = "Борҳои шумо:"
MY_PARCELS_ITEM = (
    "Трек-код: {track_code}\n"
    "Статус: {dynamic_status}\n"
    "Склад: {destination_city}\n"
    "Санаи қабул: {received_china_at}"
)

PROFILE = (
    "Профили ман\n\n"
    "Ном: {full_name}\n"
    "Телефон: {phone}\n"
    "Шаҳр: {city}\n"
    "Коди мизоҷӣ: {client_code}\n"
    "Забон: {language}\n\n"
    "Аз ин ҷо шумо метавонед маълумоти худро тағйир диҳед."
)
PROFILE_BACK = "Менюи асосӣ"
PROFILE_UPDATED = "Маълумот нав шуд."
PHONE_ALREADY_USED = "Ин рақами телефон аллакай истифода мешавад."

CALCULATOR = "Ҳисобкунак"
CALCULATOR_BY_KG = "Бо килограмм"
CALCULATOR_BY_CUBE = "Бо куб"
CALCULATOR_RESULT = "Нархи тахминӣ: {amount} сомонӣ"
CALCULATOR_CHOOSE = "Навъи ҳисобро интихоб кунед."
CALCULATOR_ASK_KG = "Вазнро бо кг ворид кунед."
CALCULATOR_ASK_CUBE = "Ҳаҷмро бо куб ворид кунед."
CALCULATOR_INVALID_NUMBER = "Лутфан рақами мусбат ворид кунед."
CALCULATOR_KG_RESULT = (
    "Ҳисоби тахминӣ\n\n"
    "Вазн: {amount} кг\n"
    "Нарх барои 1 кг: {price} сомонӣ\n"
    "Ҳамагӣ: {total} сомонӣ\n\n"
    "Ин ҳисоб тахминӣ аст. Вазн ва маблағи аниқ баъди расидани бор маълум мешавад."
)
CALCULATOR_CUBE_RESULT = (
    "Ҳисоби тахминӣ\n\n"
    "Ҳаҷм: {amount} куб\n"
    "Нарх барои 1 куб: {price} сомонӣ\n"
    "Ҳамагӣ: {total} сомонӣ\n\n"
    "Ин ҳисоб тахминӣ аст. Вазн ва маблағи аниқ баъди расидани бор маълум мешавад."
)

WAREHOUSE_ACTIVE = "{city}\n\n{caption}"
WAREHOUSE_INACTIVE = (
    "Ҳозирча барои ин минтақа склад фаъол нест.\n"
    "Лутфан варианти “Истаравшан”-ро интихоб кунед."
)

DELIVERY_UNAVAILABLE = "Ҳозирча хизматрасонии доставка фаъол нест."
DELIVERY_REQUEST = "Адреси доставкаро фиристед."
DELIVERY_REQUEST_ACCEPTED = "Дархости доставка қабул шуд."
DELIVERY_NOT_FOUND = "Бори расида барои доставка ёфт нашуд."
DELIVERY_CONFIRM = (
    "Дархости доставкаро тасдиқ кунед\n\n"
    "Трек-код: {track_code}\n"
    "Ном: {full_name}\n"
    "Телефон: {phone}\n"
    "Склад: {destination_city}\n"
    "Адрес: {delivery_address}"
)
DELIVERY_TERMS = (
    "Хизматрасонии доставка\n\n"
    "{inside_city}\n\n"
    "{outside_city}\n\n"
    "Лутфан адреси худро равон кунед:"
)
DELIVERY_SEND_ADDRESS = "Лутфан адреси худро равон кунед:"
DELIVERY_CANCELLED = "Дархости доставка бекор карда шуд."

NOTIFICATION_CHINA_RECEIVED = (
    "Бори шумо қабул шуд\n\n"
    "Трек-код: {track_code}\n"
    "Статус: {status}\n"
    "Склад: {destination_city}\n"
    "Санаи қабул дар склади Чин: {received_china_at}\n"
    "Муддати тахминии расидан: {delivery_days}\n\n"
    "Вазн ва маблағ баъди расидан маълум мешавад."
)
NOTIFICATION_ARRIVED = (
    "Бори шумо ба склади {city} расид\n\n"
    "Трек-код: {track_code}\n"
    "Статус: Омода барои гирифтан\n\n"
    "Шумо метавонед борро аз склад гирифта баред ё хизматрасонии доставка интихоб кунед."
)

OPERATOR = (
    "Барои тамос бо оператор:\n"
    "{contacts}"
)
OPERATOR_NOT_SET = "Тамоси оператор ҳоло сабт нашудааст."

PRICES = (
    "Нархҳо\n"
    "1 кг: {price_per_kg_tjs} сомонӣ\n"
    "1 куб: {price_per_cube_tjs} сомонӣ\n"
    "Муҳлати расидан: {delivery_days}"
)
