"""Database handler."""
import abc
import json
import logging
import pymysql

from aiogram import types

from bot_ai.utils.mysql_connection import Connection


class BaseHandler(abc.ABC):
    """Abstract base class for handlers."""

    @staticmethod
    @abc.abstractmethod
    async def update_analytic_datas_count_ai_queries(
            message: types.Message | types.CallbackQuery,
            count: int = 1
    ) -> None:
        """
        Update analytic datas. Update CAQ.

        :param message: Message obj.
        :param count: Count of AI queries.

        :return: None.
        """

    @staticmethod
    @abc.abstractmethod
    async def get_analytic_datas_count_ai_queries(
            telegram_id: int
    ) -> str:
        """
        Update analytic datas. Update CAQ.

        :param telegram_id: Telegram user ID.
        :return: Count of AI queries.
        """

    @staticmethod
    @abc.abstractmethod
    async def update_context(telegram_id: int, context: list) -> None:
        """
        Update context in database.

        :param telegram_id: Telegram User ID.
        :param context: Context of AI.

        :return: None.
        """

    @staticmethod
    @abc.abstractmethod
    async def get_context(telegram_id: int) -> list:
        """
        Get context from database.

        :param telegram_id: Telegram User ID.
        :return: List with data.
        """

    @staticmethod
    @abc.abstractmethod
    async def get_data(file_path="bot.json") -> dict:
        """
        Get data of the ADMIN Manager Bot.

        :param file_path: File Path of JSON-API-keys for Bot.
        :return: Dict with data.
        """


class HandlerDB(BaseHandler):
    """Handler DB class."""

    @staticmethod
    async def update_analytic_datas_count_ai_queries(
            message: types.Message | types.CallbackQuery,
            count: int = 1
    ) -> None:
        """
        Update analytic datas. Update CAQ.

        :param message: Message obj.
        :param count: Count of AI queries.

        :return: None.
        """
        telegram_username: str = message.from_user.username
        telegram_id: int = message.from_user.id
        firstname: str = message.from_user.first_name
        lastname: str = message.from_user.last_name

        connection: pymysql.Connection = await Connection.get_connection(
            await HandlerDB.get_data()
        )
        cursor = connection.cursor()

        query: str = f"""SELECT count_of_ai_queries FROM users 
        WHERE telegram_id = '{str(telegram_id)}';"""
        cursor.execute(query)
        count_of_ai_queries = cursor.fetchall()

        if len(count_of_ai_queries) == 0:
            query: str = f"""INSERT INTO users (
            telegram_id, telegram_username, firstname, lastname, count_of_ai_queries
            ) VALUES (
            '{str(telegram_id)}', '{telegram_username}', '{firstname}', 
            '{lastname}', {count});"""
            cursor.execute(query)
        else:
            query: str = f"""UPDATE users SET 
            count_of_ai_queries = %s WHERE telegram_id = %s;"""
            cursor.execute(query, (count_of_ai_queries[0][0] + count, str(telegram_id)))

        connection.commit()
        connection.close()

    @staticmethod
    async def get_analytic_datas_count_ai_queries(
            telegram_id: int
    ) -> str:
        """
        Update analytic datas. Update CAQ.

        :param telegram_id: Telegram user ID.
        :return: Count of AI queries.
        """
        connection: pymysql.Connection = await Connection.get_connection(
            await HandlerDB.get_data()
        )
        cursor = connection.cursor()

        query: str = f"""SELECT count_of_ai_queries FROM users 
                     WHERE telegram_id = '{str(telegram_id)}';"""
        cursor.execute(query)
        count_of_ai_queries = cursor.fetchall()

        connection.close()

        if len(count_of_ai_queries) == 0:
            return "0"
        else:
            return str(count_of_ai_queries[0][0])

    @staticmethod
    async def update_context(telegram_id: int, context: list) -> None:
        """
        Update context in database.

        :param telegram_id: Telegram User ID.
        :param context: Context AI.

        :return: None.
        """
        connection: pymysql.Connection = await Connection.get_connection(
            await HandlerDB.get_data()
        )
        cursor = connection.cursor()
        query: str = f"""UPDATE users SET 
                     context = %s WHERE telegram_id = %s;"""
        cursor.execute(query, (json.dumps({"data": context}).encode("utf-8"), str(telegram_id),))

        connection.commit()
        connection.close()

    @staticmethod
    async def get_context(telegram_id: int) -> list:
        """
        Get context from database.

        :param telegram_id: Telegram User ID.
        :return: List with data.
        """
        connection: pymysql.Connection = await Connection.get_connection(
            await HandlerDB.get_data()
        )
        cursor = connection.cursor()

        query: str = f"""SELECT context FROM users 
                     WHERE telegram_id = '{str(telegram_id)}';"""
        cursor.execute(query)
        context = cursor.fetchall()

        if context[0][0] is None:
            return [
                {
                    "role": "system",
                    "content": "You're an AI assistant integrated from SBER's GigaChat API."
                }
            ]

        else:
            messages = json.loads(context[0][0])
            return messages["data"]

    @staticmethod
    async def get_data(file_path="bot.json") -> dict:
        """
        Get data of the ADMIN Manager Bot.

        :param file_path: File Path of JSON-API-keys for Bot.
        :return: Dict with data.
        """
        with open(file_path, "r", encoding='utf-8') as file:
            data: dict = json.load(file)

            dct = dict()

            dct["MYSQL"] = data["MYSQL"]

            logging.info(
                "Obtained MySQL DB data from the conf. file for communication with the database"
            )

            return dct["MYSQL"]
