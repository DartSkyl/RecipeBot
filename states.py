from aiogram.fsm.state import StatesGroup, State


class Admin(StatesGroup):
    add_link_name = State()
    add_link_url = State()
    remove_link = State()
