import asyncio
import logging
import sys
from datetime import date
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from dotenv import load_dotenv
from peewee import IntegrityError

from database.common.models import User, db, History
from database.core import crud
from site_API.core import get_low, get_high, get_custom
from tg_API.utils.config import Low, High, Custom

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(Command("start"))
async def command_start(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        await message.answer("Welcome to movies database!")
    except IntegrityError:
        await message.answer(f"Glad to see you again, {first_name}!")


@dp.message(Command("helloworld"))
async def command_helloworld(message: Message) -> None:
    await message.answer(f"Hello, world!")


@dp.message(F.text == "Hi!")
async def send_hi(message: Message) -> None:
    await message.send_copy(message.chat.id)


@dp.message(Command("low"))
async def command_low(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        await message.answer("You are not registered. Write /start")
        return
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
    user = User.get_or_none(User.user_id == message.from_user.id)
    db_data = list()
    if answers:
        for movie in answers:
            printed_movie = str()
            for key, value in movie.items():
                if key != "Ratings":
                    printed_movie += f"<b>{key}</b>: {value}\n"
            db_data.append({"movie": printed_movie, "user": user, "date": date.today()})
            storing = crud.store()
            storing(db, History, db_data)
            await message.answer(printed_movie)
        await message.answer("The end.")
        await state.clear()
    else:
        await message.answer("Please specify your request.", parse_mode="HTML")
        await state.set_state(Low.title)


@dp.message(Command("high"))
async def command_high(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        await message.answer("You are not registered. Write /start")
        return
    await state.set_state(High.title)
    await message.answer("Enter title for search.",
                         reply_markup=ReplyKeyboardRemove())


@dp.message(High.title)
async def save_high_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(High.amount)
    await message.answer("Enter the amount of responses.")


@dp.message(High.amount)
async def save_high_amount(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit():
        await message.answer("Something went wrong. Try again.")
        return
    elif int(message.text) < 1:
        await message.answer("Amount of responses should be higher than 1.")
        return
    data = await state.get_data()
    answers = get_high(data["title"], int(message.text))
    user = User.get_or_none(User.user_id == message.from_user.id)
    db_data = list()
    if answers:
        for movie in answers:
            printed_movie = str()
            for key, value in movie.items():
                if key != "Ratings":
                    printed_movie += f"<b>{key}</b>: {value}\n"
            db_data.append({"movie": printed_movie, "user": user, "date": date.today()})
            storing = crud.store()
            storing(db, History, db_data)
            await message.answer(printed_movie)
        await message.answer("The end.")
        await state.clear()
    else:
        await message.answer("Please specify your request.", parse_mode="HTML")
        await state.set_state(High.title)


@dp.message(Command("custom"))
async def command_custom(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        await message.answer("You are not registered. Write /start")
        return
    await state.set_state(Custom.title)
    await message.answer("Enter title for search.",
                         reply_markup=ReplyKeyboardRemove())


@dp.message(Custom.title)
async def save_custom_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(Custom.min)
    await message.answer("Enter the minimal imdb rating.")


@dp.message(Custom.min)
async def save_min_title(message:Message, state: FSMContext) -> None:
    try:
        min_rating = float(message.text)
    except TypeError:
        await message.answer("Something went wrong, try again.")
        return
    if 0 <= min_rating < 10:
        await state.update_data(min=min_rating)
        await state.set_state(Custom.max)
        await message.answer("Enter the maximal imdb rating.")
    else:
        await message.answer("Rating should be from 0 to 10. Try again.")


@dp.message(Custom.max)
async def save_min_title(message: Message, state: FSMContext) -> None:
    try:
        max_rating = float(message.text)
    except TypeError:
        await message.answer("Something went wrong, try again.")
        return
    if 0 < max_rating <= 10:
        await state.update_data(max=max_rating)
        await state.set_state(Custom.amount)
        await message.answer("Enter the amount of responses.")
    else:
        await message.answer("Rating should be from 0 to 10. Try again.")


@dp.message(Custom.amount)
async def save_custom_amount(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit():
        await message.answer("Something went wrong. Try again.")
        return
    elif int(message.text) < 1:
        await message.answer("Amount of responses should be higher than 1.")
        return
    data = await state.get_data()
    answers = get_custom(data["title"], data["min"], data["max"], int(message.text))
    user = User.get_or_none(User.user_id == message.from_user.id)
    db_data = list()
    if answers:
        for movie in answers:
            printed_movie = str()
            for key, value in movie.items():
                if key != "Ratings":
                    printed_movie += f"<b>{key}</b>: {value}\n"
            db_data.append({"movie": printed_movie, "user": user, "date": date.today()})
            storing = crud.store()
            storing(db, History, db_data)
            await message.answer(printed_movie)
        await message.answer("The end.")
        await state.clear()
    else:
        await message.answer("Please specify your request.", parse_mode="HTML")
        await state.set_state(Custom.title)


@dp.message(Command("history"))
async def history(message: Message) -> None:
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        await message.answer("You are not registered. Write /start")
        return
    user_history: list[History] = user.history.order_by(-History.date)
    result = [record.movie for record in user_history]
    for title in result:
        await message.answer(title, parse_mode="html")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed
    # to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
