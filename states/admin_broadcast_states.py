from aiogram.fsm.state import State, StatesGroup


class AdminBroadcastStates(StatesGroup):
    choosing_language = State()
    choosing_filter = State()
    choosing_status = State()
    choosing_date_field = State()
    waiting_for_date = State()
    waiting_for_telegram_id = State()
    waiting_for_track_code = State()
    waiting_for_content = State()
    confirming = State()
