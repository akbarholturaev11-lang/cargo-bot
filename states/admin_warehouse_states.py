from aiogram.fsm.state import State, StatesGroup


class AdminWarehouseStates(StatesGroup):
    choosing_city = State()
    waiting_for_photo_caption = State()
    waiting_for_caption = State()
    waiting_for_photo = State()
    confirming = State()
    choosing_inactive_city = State()
