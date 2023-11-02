import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(Command("helloworld"))
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, world!")


@dp.message(F.text == "Hi!")
async def send_hi(message: Message) -> None:
    await message.send_copy(message.chat.id)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed
    # to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
