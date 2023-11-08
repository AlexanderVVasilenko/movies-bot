import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from site_API.core import get_low
from tg_API.utils.config import Low, High, Custom

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(Command("helloworld"))
async def command_helloworld(message: Message) -> None:
    await message.answer(f"Hello, world!")


@dp.message(F.text == "Hi!")
async def send_hi(message: Message) -> None:
    await message.send_copy(message.chat.id)


@dp.message(Command("low"))
async def command_low(message: Message, state: FSMContext) -> None:
    await state.set_state(Low.title)
    await message.answer("Enter title for search.",
                         reply_markup=ReplyKeyboardRemove())


@dp.message(Low.title)
async def save_low_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(Low.amount)
    await message.answer("Enter the amount of responses.")


@dp.message(Low.amount)
async def save_low_amount(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit():
        await message.answer("Something went wrong. Try again.")
        return
    elif int(message.text) < 1:
        await message.answer("Amount of responses should be higher than 1.")
        return
    data = await state.get_data()
    answers = get_low(data["title"], int(message.text))
    if answers:
        for movie in answers:
            await message.answer(str(movie))
        await message.answer("The end.")
        await state.clear()
    else:
        await message.answer("Please specify your request.")
        await state.set_state(Low.title)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed
    # to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
