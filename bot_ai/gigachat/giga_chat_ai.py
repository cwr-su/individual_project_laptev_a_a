"""Giga Chat AI."""

from bot_ai.states import GetQuery
import abc
import logging
from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from bot_ai.buttons import Buttons
from bot_ai.gigachat.giga_requests import VersionAIPro
from bot_ai.utils.handler_db import HandlerDB

router_chat_ai: Router = Router()

messages: list = [
    {
        "role": "system",
        "content": "Ты ИИ ассистент интегрированный из GigaChat API от SBER."
    }
]


class BaseUpdateMessages(abc.ABC):
    """Base class for update messages."""

    @staticmethod
    @abc.abstractmethod
    def update_messages(role: str, content: str) -> None:
        """
        The method for update messages.

        :param role: Role of message.
        :param content: Content of message.
        :return: None.
        """


class UpdateMessages(BaseUpdateMessages):
    """The class for update messages."""

    @staticmethod
    @abc.abstractmethod
    def update_messages(role: str, content: str) -> None:
        """
        The method for update messages.

        :param role: Role of message.
        :param content: Content of message.
        :return: None.
        """
        try:
            if len(messages) >= 8:
                messages.pop(1)

            messages.append(
                {
                    "role": role,
                    "content": content
                }
            )
        except Exception as ex:
            logging.error(
                f"Error in update messages: {ex}"
            )
            messages.append(
                {
                    "role": role,
                    "content": content
                }
            )


class GigaChatAI:
    """
    The class for giga chat AI.
    """

    def __init__(self, bot: Bot) -> None:
        self.__bot: Bot = bot

        router_chat_ai.message.register(
            self.__chat_dialog_ai,
            GetQuery.query
        )

    async def giga_chat_ai(self, callback_query: types.CallbackQuery, state: FSMContext) -> None:
        """
        The method for manage chat dialog with AI.

        :param callback_query: Callback query object.
        :param state: State object.

        :return: None.
        """
        await state.set_state(GetQuery.query)

        await self.__bot.edit_message_text(
            text="Hello! I'm ready to help you! What question are you interested in? 😎\n\n"
                 "_STOP-Command_: `//stop`.",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            parse_mode="Markdown"
        )

        logging.info(
            "AI dialogue in PRO mode - activated!"
        )

    async def __chat_dialog_ai(self, message: types.Message, state: FSMContext) -> None:
        """
        The method for manage chat dialog with AI.

        :param message: The message object.
        :param state: FSM.

        :return: None.
        """
        cd: BaseChatDialog = ChatDialogGigaVersionPro(self.__bot)
        await cd.chat_dialog(message, state)


class BaseChatDialog(abc.ABC):
    """
    The class for Chat-Dialog function (Base Class-Sector).
    """

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @abc.abstractmethod
    async def chat_dialog(self, message: types.Message, state: FSMContext) -> None:
        """
        Basic Chat-Dialog function.

        :param message: Message of user / query.
        :param state: FSM.

        :return: None.
        """


class ChatDialogGigaVersionPro(BaseChatDialog):
    """
    The class for Chat-Dialog function (GigaPro V. dialog).
    """

    async def chat_dialog(self, message: types.Message, state: FSMContext) -> None:
        """
        GLV Chat-Dialog function.

        :param message: Message of user / query.
        :param state: FSM.

        :return: None.
        """
        if message.text.lower() != "//stop":
            router_chat_ai.message.register(
                ChatDialogGigaVersionPro.chat_dialog,
                GetQuery.query
            )

            UpdateMessages.update_messages("user", message.text)
            response: str = await VersionAIPro.request(messages, message.from_user.id)

            await self.bot.send_message(
                text=response,
                chat_id=message.from_user.id,
                parse_mode="Markdown",
            )

            UpdateMessages.update_messages("assistant", response)

            await HandlerDB.update_analytic_datas_count_ai_queries(message)

            await state.clear()
            new_state: NewFSMContextPro = NewFSMContextPro(self.bot)
            await new_state.set(state)

        else:
            var: InlineKeyboardBuilder = await Buttons.create(
                {"🌐 Main": "back_on_main"}
            )
            await self.bot.send_message(
                text=f"Got it! I have stopped (AI-Chat Dialog-PRO).",
                chat_id=message.from_user.id,
                parse_mode="Markdown",
                reply_markup=var.as_markup()
            )

            await state.clear()

            logging.info(
                "AI dialogue in PRO mode - deactivated!"
            )


class BaseNewFSMContext(abc.ABC):
    """
    The base-class for create new state (FSM).
    """

    def __init__(self, bot: Bot) -> None:
        self.__bot: Bot = bot

    @abc.abstractmethod
    async def set(self, state: FSMContext) -> None:
        """
        Set state.

        :param state: FSM.
        :return: None.
        """

    @abc.abstractmethod
    async def chat_dialog(self, message: types.Message, state: FSMContext) -> None:
        """
        Chat-Dialog function.

        :param message: Message of user / query.
        :param state: FSM.

        :return: None.
        """


class NewFSMContextPro(BaseNewFSMContext):
    """
    The class for create new state (FSM) - GVL.
    """

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        router_chat_ai.message.register(
            self.chat_dialog,
            GetQuery.query
        )

    async def set(self, state: FSMContext) -> None:
        """
        Set state.

        :param state: FSM.
        :return: None.
        """
        await state.set_state(GetQuery.query)

    async def chat_dialog(self, message: types.Message, state: FSMContext) -> None:
        """
        GLV Chat-Dialog function.

        :param message: Message of user / query.
        :param state: FSM.

        :return: None.
        """
        cd: ChatDialogGigaVersionPro = ChatDialogGigaVersionPro(self.__bot)
        await cd.chat_dialog(message, state)
