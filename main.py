"""Main module."""
import asyncio
import logging
import sys
from bot_ai.bot import run


class Main:
    """Main class."""
    @staticmethod
    async def main() -> None:
        """
        Main function.

        :return: None.
        """
        await run()


async def main() -> None:
    """Main function."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(asctime)s -- %(funcName)s -- %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        stream=sys.stdout
    )

    logging.info(
        f"Start main-function in the main module"
    )
    await Main.main()


if __name__ == "__main__":
    asyncio.run(main())
