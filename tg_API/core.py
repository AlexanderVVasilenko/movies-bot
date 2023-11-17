import asyncio
import logging
import sys
from datetime import date
from os import getenv

from aiogram import Bot, Dispatcher
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

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


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


async def handle_commands(message: Message, state: FSMContext, search_type, title_state, amount_state):
    user_id = message.from_user.id
    user = User.get_or_none(User.user_id == user_id)
    if user is None:
        await message.answer("You are not registered. Write /start")
        return
    await state.set_state(title_state)
    await message.answer(f"Enter title for {search_type} search.", reply_markup=ReplyKeyboardRemove())


@dp.message(Command("low"))
async def command_low(message: Message, state: FSMContext) -> None:
    await handle_commands(message, state, "low", Low.title, Low.amount)


@dp.message(Low.title)
async def save_low_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(Low.amount)
    await message.answer("Enter the amount of responses.")


@dp.message(Low.amount)
async def save_low_amount(message: Message, state: FSMContext) -> None:
    await save_responses(message, state, get_low, Low.title)


@dp.message(Command("high"))
async def command_high(message: Message, state: FSMContext) -> None:
    await handle_commands(message, state, "high", High.title, High.amount)


@dp.message(High.title)
async def save_high_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(High.amount)
    await message.answer("Enter the amount of responses.")


@dp.message(High.amount)
async def save_high_amount(message: Message, state: FSMContext) -> None:
    await save_responses(message, state, get_high, High.title)


@dp.message(Command("custom"))
async def command_custom(message: Message, state: FSMContext) -> None:
    await handle_commands(message, state, "custom", Custom.title, Custom.min)


@dp.message(Custom.title)
async def save_custom_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(Custom.min)
    await message.answer("Enter the minimal imdb rating.")


@dp.message(Custom.min)
async def save_min_title(message: Message, state: FSMContext) -> None:
    await save_rating(message, state, "min", Custom.max)


@dp.message(Custom.max)
async def save_min_title(message: Message, state: FSMContext) -> None:
    await save_rating(message, state, "max", Custom.amount)


@dp.message(Custom.amount)
async def save_custom_amount(message: Message, state: FSMContext) -> None:
    await save_responses(message, state, get_custom, Custom.title)


async def save_rating(message: Message, state: FSMContext, rating_key, next_state):
    try:
        rating = float(message.text)
    except TypeError:
        await message.answer("Something went wrong, try again.")
        return
    if 0 <= rating <= 10:
        await state.update_data({rating_key: rating})
        await state.set_state(next_state)
        await message.answer(f"Enter the {'maximal' if rating_key == 'max' else 'minimal'} imdb rating.")
    else:
        await message.answer("Rating should be from 0 to 10. Try again.")


async def save_responses(message: Message, state: FSMContext, search_function, title_state):
    if not message.text.isdigit():
        await message.answer("Something went wrong. Try again.")
        return
    elif int(message.text) < 1:
        await message.answer("Amount of responses should be higher than 1.")
        return
    data = await state.get_data()
    answers = search_function(data["title"], int(message.text))
    user = User.get_or_none(User.user_id == message.from_user.id)
    db_data = list()
    if answers:
        for movie in answers:
            printed_movie = "\n".join([f"<b>{key}</b>: {value}" for key, value in movie.items() if key != "Ratings"])
            db_data.append({"movie": printed_movie, "user": user, "date": date.today()})
            storing = crud.store()
            storing(db, History, db_data)
            await message.answer(printed_movie)
        await message.answer("The end.")
        await state.clear()
    else:
        await message.answer("Please specify your request.", parse_mode="HTML")
        await state.set_state(title_state)


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
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
