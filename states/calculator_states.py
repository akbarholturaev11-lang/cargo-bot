from aiogram.fsm.state import State, StatesGroup


class CalculatorStates(StatesGroup):
    waiting_for_kg = State()
    waiting_for_cube = State()
