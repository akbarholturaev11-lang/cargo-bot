from aiogram.fsm.state import State, StatesGroup


class AdminBulkStatusStates(StatesGroup):
    choosing_city = State()
    waiting_for_batch_date = State()
    choosing_old_status = State()
    choosing_new_status = State()
    confirming = State()
