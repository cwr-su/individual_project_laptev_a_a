"""Main module of the bot."""
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

import json
import abc
import logging
import pymysql

from bot_ai.buttons import Buttons
from bot_ai.utils.create_table import CreateTable
from bot_ai.utils.mysql_connection import Connection
from bot_ai.gigachat.giga_chat_ai import router_chat_ai, GigaChatAI
from bot_ai.utils.handler_db import HandlerDB


class BasicMethod(abc.ABC):
    """Base class for basic method of the Bot."""

    @staticmethod
    @abc.abstractmethod
    async def method(bot: Bot, message: Message | CallbackQuery) -> None:
        """
        The basic method of answer to the message.

        :param bot: The Bot Object.
        :param message: The message object.
        :type message: Message | CallbackQuery.

        :return: None.
        """


class StartCommand(BasicMethod):
    """The class-sector for manage command start."""

    @staticmethod
    async def method(bot: Bot, message: Message | CallbackQuery) -> None:
        """
        The method for manage start cmd (command).

        :param bot: The Bot Object.
        :param message: The message object.
        :type message: Message | CallbackQuery.

        :return: None.
        """
        button: InlineKeyboardBuilder = await Buttons.create(
            data={
                "Start Chat Dialog with AI": "start_chat_dialog_ai",
                "View analytics": "view_analytics"
            }
        )
        await bot.send_message(
            text=f"Hello 👀!\n"
                 f"*{message.from_user.first_name}*, to start either AI model 🧠 - click on the "
                 f"corresponding button below.",
            chat_id=message.from_user.id,
            reply_markup=button.as_markup(),
            parse_mode="Markdown"
        )


class BackOnMain(BasicMethod):
    """Class for the move to the main-menu."""
    @staticmethod
    async def method(bot: Bot, callback_query: Message | CallbackQuery) -> None:
        """
        The method for manage main-btn cmd (command).

        :param bot: The Bot Object.
        :param callback_query: The Callback Query object.
        :type callback_query: Message | CallbackQuery.

        :return: None.
        """
        button: InlineKeyboardBuilder = await Buttons.create(
            data={
                "Start Chat Dialog with AI": "start_chat_dialog_ai",
                "View analytics": "view_analytics"
            }
        )
        await bot.edit_message_text(
            text=f"🌐 Main-menu\n"
                 f"*{callback_query.from_user.first_name}*, to start either AI model 🧠 - click "
                 f"on the corresponding button below.",
            chat_id=callback_query.from_user.id,
            reply_markup=button.as_markup(),
            parse_mode="Markdown",
            message_id=callback_query.message.message_id
        )


class ViewAnalytics(BasicMethod):
    """Class for the move to the analytics menu."""
    @staticmethod
    async def method(bot: Bot, callback_query: Message | CallbackQuery) -> None:
        """
        The method for view analytics cmd (command).

        :param bot: The Bot Object.
        :param callback_query: The Callback Query object.
        :type callback_query: Message | CallbackQuery.

        :return: None.
        """
        button: InlineKeyboardBuilder = await Buttons.create(
            data={
                "Back to main menu 🌐": "back_on_main"
            }
        )
        await bot.edit_message_text(
            text=f"💻 Analytics\n"
                 f"*{callback_query.from_user.first_name}*, you used "
                 f"{await HandlerDB.get_analytic_datas_count_ai_queries(
                     callback_query.from_user.id
                 )} "
                 f"requests.\n\n"
                 f"To back to main menu - click on the "
                 f"corresponding button below.",
            chat_id=callback_query.from_user.id,
            reply_markup=button.as_markup(),
            parse_mode="Markdown",
            message_id=callback_query.message.message_id
        )


class BotAI(Bot):
    def __init__(self, token: str, mysql_data: dict):
        super().__init__(token)
        self.__dispatcher: Dispatcher = Dispatcher()
        self.__router: Router = Router()

        self.__mysql_data: dict = mysql_data

    async def __start_command(self, message: Message) -> None:
        """
        The method for manage start cmd (command).

        :param message: The message object.
        :type message: Message.

        :return: None.
        """
        await StartCommand.method(
            self, message
        )
        self.__dispatcher.callback_query.register(
            self.__start_chat_dialog_ai,
            F.data == "start_chat_dialog_ai"
        )

    async def __start_chat_dialog_ai(
            self,
            callback_query: CallbackQuery,
            state: FSMContext
    ) -> None:
        """
        This method is used to move to the language AI model version selection menu.

        :param callback_query: Callback Query.
        :param state: State.
        :return: None.
        """
        giga_chat_ai: GigaChatAI = GigaChatAI(
            self
        )
        await giga_chat_ai.giga_chat_ai(callback_query, state)

    async def __back_on_main(
            self,
            callback_query: CallbackQuery,
    ) -> None:
        """
        This method is used to move to the MAIN menu.

        :param callback_query: Callback Query.
        :return: None.
        """
        await BackOnMain.method(self, callback_query)

    async def __view_analytics(
            self,
            callback_query: CallbackQuery,
    ) -> None:
        """
        This method is used to move to the analytics menu.
        :param callback_query: Callback Query.
        :return: None.
        """
        await ViewAnalytics.method(self, callback_query)

    async def run(self) -> None:
        """
        Run function for register routers and methods.

        :return: None.
        """
        connection: pymysql.connections.Connection = await Connection.get_connection(
            self.__mysql_data
        )
        cursor = connection.cursor()

        table: CreateTable = CreateTable(
            connection, cursor
        )
        table.create()

        logging.info(
            f"The table has been created successfully! "
            f"Starting registering methods and commands..."
        )
        self.__router.message.register(
            self.__start_command,
            Command(commands=["start", "main"])
        )

        self.__router.callback_query.register(
            self.__start_chat_dialog_ai,
            F.data == "start_chat_dialog_ai"
        )
        self.__router.callback_query.register(
            self.__back_on_main,
            F.data == "back_on_main"
        )
        self.__router.callback_query.register(
            self.__view_analytics,
            F.data == "view_analytics"
        )

        self.__dispatcher.include_routers(
            self.__router, router_chat_ai
        )

        logging.info(
            f"I have ended registering methods and commands already"
        )

        await self.__dispatcher.start_polling(self)

        logging.info(
            f"The bot is up and running"
        )


class BaseGetData(abc.ABC):
    """Base class for getting data from .json-file."""

    @staticmethod
    @abc.abstractmethod
    async def get_data(file_path: str) -> dict:
        """
        Get data from base file by definitely file path.

        :param file_path: File path.
        :return: Dict-data.
        """


class GetData(BaseGetData):
    """Get data from bot.json-file."""

    @staticmethod
    async def get_data(file_path: str = "bot.json") -> dict:
        """
        Get data from file by definitely bot.json-file.

        :param file_path: bot.json path.
        :return: Dict-data.
        """
        with open(file_path, "r") as file:
            data: dict = json.load(file)
            result_dict: dict = {
                "BOT_TOKEN": data["BOT_TOKEN"],
                "MYSQL": data["MYSQL"]
            }

            return result_dict


async def run() -> None:
    """
    Run function.

    :return: None.
    """
    data: dict = await GetData.get_data()
    bot: BotAI = BotAI(
        data["BOT_TOKEN"],
        data["MYSQL"]
    )
    await bot.run()
