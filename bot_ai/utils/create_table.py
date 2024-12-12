"""Module for create table in DataBase."""
import pymysql
import abc


class BaseCreateTable(abc.ABC):
    """Base class-sector for create table."""
    def __init__(
        self,
        connection: pymysql.connections.Connection,
        cursor
    ):
        self._connection: pymysql.connections.Connection = connection
        self._cursor = cursor

    @abc.abstractmethod
    def create(self) -> None:
        """
        Create-function.

        :return: None.
        """


class CreateTable(BaseCreateTable):
    """Creator-class for create table in database (mysql)."""

    def create(self) -> None:
        """
        Create-function.

        :return: None.
        """

        query: str = f"""CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            telegram_id VARCHAR (255) UNIQUE NOT NULL,
            telegram_username VARCHAR(255) UNIQUE NOT NULL,
            firstname VARCHAR (255) NOT NULL,
            lastname VARCHAR (255) NOT NULL,
            context LONGTEXT,
            count_of_ai_queries INT NOT NULL
            );
            """
        self._cursor.execute(query)

        self._connection.commit()
        self._connection.close()
