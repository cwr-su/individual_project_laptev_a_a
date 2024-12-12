"""Module of the FSM-classes."""
from aiogram.fsm.state import State, StatesGroup


class GetQuery(StatesGroup):
    """States for getting query for text-generations."""
    query: State = State()


class GigaImage(StatesGroup):
    """States for getting query-request for image-generations."""
    request: State = State()
