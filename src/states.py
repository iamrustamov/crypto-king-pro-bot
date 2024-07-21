from aiogram.fsm.state import StatesGroup, State


class TextEdit(StatesGroup):
    new_text = State()


class PowerInput(StatesGroup):
    power = State()
