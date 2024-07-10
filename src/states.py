from aiogram.fsm.state import StatesGroup, State


class TextEdit(StatesGroup):
    new_text = State()
