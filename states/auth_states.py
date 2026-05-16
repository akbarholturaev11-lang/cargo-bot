from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    choosing_language = State()
    choosing_auth_action = State()
    register_full_name = State()
    register_phone = State()
    register_city = State()
    login_phone = State()
    login_full_name = State()
