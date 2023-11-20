from aiogram.fsm.state import StatesGroup, State


class Low(StatesGroup):
    title = State()
    amount = State()


class High(StatesGroup):
    title = State()
    amount = State()


class Custom(StatesGroup):
    title = State()
    min = State()
    max = State()
    amount = State()
