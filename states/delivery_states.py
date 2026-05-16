from aiogram.fsm.state import State, StatesGroup


class DeliveryStates(StatesGroup):
    waiting_for_address = State()
    confirming = State()
