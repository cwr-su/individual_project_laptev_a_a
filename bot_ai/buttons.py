"""Module for getting buttons."""
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import abc


class BaseButtonsCallData(abc.ABC):
    """Basic sector for create buttons with some callback data."""

    @staticmethod
    @abc.abstractmethod
    async def create(data: dict) -> InlineKeyboardBuilder:
        """
        Basic method for create buttons.

        :param data: Dict with data.
        :return: InlineKeyboardBuilder (Markup).
        """


class Buttons(BaseButtonsCallData):
    """Create buttons with callback data."""

    @staticmethod
    async def create(data: dict) -> InlineKeyboardBuilder:
        """
        The method for create buttons by callback data.

        :param data: Dict with data.
        :return: InlineKeyboardBuilder (Markup).
        """
        builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

        for key, value in data.items():
            button: InlineKeyboardButton = InlineKeyboardButton(
                text=f"{key}",
                callback_data=f"{value}"
            )
            builder.row(button)

        return builder
