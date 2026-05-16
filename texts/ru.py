CHOOSE_LANGUAGE = "Выберите язык:"

REGISTER = "Регистрация"
LOGIN = "Войти"

ASK_FULL_NAME = "Введите полное имя и фамилию."
ASK_PHONE = "Отправьте номер телефона кнопкой ниже."
ASK_CITY = "Выберите ваш город."

REGISTRATION_COMPLETED = (
    "Регистрация завершена.\n"
    "Ваш клиентский код: {client_code}"
)
LOGIN_SUCCESS = "Вы вошли в аккаунт."
PHONE_NOT_FOUND = (
    "❌ Этот номер не найден в базе.\n"
    "Введите номер правильно или сначала зарегистрируйтесь."
)
NAME_MISMATCH = (
    "❌ Имя и фамилия не совпали.\n"
    "Пожалуйста, введите заново."
)
INVALID_PHONE = (
    "❌ Неверный номер телефона.\n\n"
    "Введите номер только из 9 цифр.\n"
    "Пример: 929999999"
)
BACK = "Назад"

MENU_SEARCH_PARCEL = "Найти груз"
MENU_MY_PARCELS = "Мои грузы"
MENU_CALCULATOR = "Примерный расчёт"
MENU_PROFILE = "Мой профиль"
MENU_WAREHOUSES = "Адреса складов"
MENU_PRICES = "Цены"
MENU_OPERATOR = "Оператор"

PARCEL_FOUND = (
    "Ваш груз найден\n\n"
    "Трек-код: {track_code}\n"
    "Статус: {dynamic_status}\n"
    "Склад: {destination_city}\n"
    "Дата приёма на складе в Китае: {received_china_at}\n"
    "Примерный срок доставки: {delivery_days}\n\n"
    "Вес и сумма будут известны после прибытия."
)
ASK_TRACK_CODE = "Отправьте трек-код груза."
PARCEL_NOT_FOUND = "Этот трек-код не найден."

MY_PARCELS_EMPTY = "Для вас пока нет зарегистрированных грузов."
MY_PARCELS_TITLE = "Ваши грузы:"
MY_PARCELS_ITEM = (
    "Трек-код: {track_code}\n"
    "Статус: {dynamic_status}\n"
    "Склад: {destination_city}\n"
    "Дата приёма: {received_china_at}"
)

PROFILE = (
    "👤 Мой профиль\n\n"
    "Имя: {full_name}\n"
    "Телефон: {phone}\n"
    "Город: {city}\n"
    "Клиентский код: {client_code}\n"
    "Язык: {language}\n\n"
    "Здесь вы можете изменить свои данные."
)
PROFILE_BACK = "Главное меню"
PROFILE_UPDATED = "Данные обновлены."
PHONE_ALREADY_USED = "Этот номер телефона уже используется."

CALCULATOR = "Калькулятор"
CALCULATOR_BY_KG = "По килограммам"
CALCULATOR_BY_CUBE = "По кубам"
CALCULATOR_RESULT = "Примерная стоимость: {amount} сомонӣ"
CALCULATOR_CHOOSE = "Выберите тип расчёта."
CALCULATOR_ASK_KG = "Введите вес в кг."
CALCULATOR_ASK_CUBE = "Введите объём в кубах."
CALCULATOR_INVALID_NUMBER = "Пожалуйста, введите положительное число."
CALCULATOR_KG_RESULT = (
    "Примерный расчёт\n\n"
    "Вес: {amount} кг\n"
    "Цена за 1 кг: {price} сомонӣ\n"
    "Итого: {total} сомонӣ\n\n"
    "Этот расчёт примерный. Точный вес и сумма будут известны после прибытия груза."
)
CALCULATOR_CUBE_RESULT = (
    "Примерный расчёт\n\n"
    "Объём: {amount} куб\n"
    "Цена за 1 куб: {price} сомонӣ\n"
    "Итого: {total} сомонӣ\n\n"
    "Этот расчёт примерный. Точный вес и сумма будут известны после прибытия груза."
)

WAREHOUSE_ACTIVE = "{city}\n\n{caption}"
WAREHOUSE_INACTIVE = (
    "❌ Сейчас для этого региона склад недоступен.\n\n"
    "Пожалуйста, выберите вариант “Истаравшан”."
)

DELIVERY_UNAVAILABLE = "Сейчас услуга доставки недоступна."
DELIVERY_REQUEST = "Отправьте адрес доставки."
DELIVERY_REQUEST_ACCEPTED = "Заявка на доставку принята."
DELIVERY_NOT_FOUND = "Прибывший груз для доставки не найден."
DELIVERY_CONFIRM = (
    "Подтвердите заявку на доставку\n\n"
    "Трек-код: {track_code}\n"
    "Имя: {full_name}\n"
    "Телефон: {phone}\n"
    "Склад: {destination_city}\n"
    "Адрес: {delivery_address}"
)
DELIVERY_TERMS = (
    "Услуга доставки\n\n"
    "{inside_city}\n\n"
    "{outside_city}\n\n"
    "Пожалуйста, отправьте ваш адрес:"
)
DELIVERY_SEND_ADDRESS = "Пожалуйста, отправьте ваш адрес:"
DELIVERY_CANCELLED = "Заявка на доставку отменена."

NOTIFICATION_CHINA_RECEIVED = (
    "Ваш груз принят\n\n"
    "Трек-код: {track_code}\n"
    "Статус: {status}\n"
    "Склад: {destination_city}\n"
    "Дата приёма на складе в Китае: {received_china_at}\n"
    "Примерный срок доставки: {delivery_days}\n\n"
    "Вес и сумма будут известны после прибытия."
)
NOTIFICATION_ARRIVED = (
    "Ваш груз прибыл на склад {city}\n\n"
    "Трек-код: {track_code}\n"
    "Статус: Готов к получению\n\n"
    "Вы можете забрать груз со склада или выбрать услугу доставки."
)

OPERATOR = (
    "Для связи с оператором:\n"
    "{contacts}"
)
OPERATOR_NOT_SET = "Контакты оператора пока не указаны."

PRICES = (
    "Цены\n"
    "1 кг: {price_per_kg_tjs} сомонӣ\n"
    "1 куб: {price_per_cube_tjs} сомонӣ\n"
    "Срок доставки: {delivery_days}"
)
