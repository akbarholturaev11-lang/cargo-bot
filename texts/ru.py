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
PHONE_NOT_FOUND = "Этот номер телефона не найден в базе."
NAME_MISMATCH = "Имя и фамилия не совпали с номером телефона."

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
    "Мой профиль\n\n"
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
    "В этом регионе пока нет активного склада.\n"
    "Пожалуйста, выберите Истаравшан."
)

DELIVERY_UNAVAILABLE = "Сейчас услуга доставки недоступна."
DELIVERY_REQUEST = "Отправьте адрес доставки."
DELIVERY_REQUEST_ACCEPTED = "Заявка на доставку принята."

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
