"""Module of the FSM-classes."""
from aiogram.fsm.state import State, StatesGroup


class GetQuery(StatesGroup):
    query: State = State()