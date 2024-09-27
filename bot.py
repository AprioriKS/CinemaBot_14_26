import asyncio
import logging
import sys
import json

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile
from config import BOT_TOKEN as TOKEN
from commands import (FILMS_COMMAND,
                      FILMS_COMMAND_BOT,
                      START_COMMAND_BOT,
                      CREATE_COMMAND_BOT,
                      )
from keyboards import films_keyboard_markup, FilmCallback
from model import Film

# Bot token can be obtained via https://t.me/BotFather

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    print(f"{message.from_user.id=} {message.from_user.full_name=} {message.from_user.first_name=} "
          f"{message.from_user.last_name=} {message.from_user.username=} {message.from_user.is_premium=}")
    await message.answer(
        f"Вітаю, {html.bold(message.from_user.full_name)}!\nЯ перший бот розробника Костянтина Бугайова")


@dp.message(FILMS_COMMAND)
async def films_handler(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(film_list=data)
    await message.answer(
        f"Список фільмів. Натисніть на назву для деталей", reply_markup=markup
    )


@dp.callback_query(FilmCallback.filter())
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_id = callback_data.id
    film_data = get_films(film_id=film_id)
    film = Film(**film_data)

    text = f"Фільм: {film.name}\n" \
           f"Опис: {film.description}\n" \
           f"Рейтинг: {film.rating}\n" \
           f"Жанр: {film.genre}\n" \
           f"Актори: {', '.join(film.actors)}\n"

    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(film.poster,
                           filename=f"{film.name}_poster.{film.poster.split('.')[-1]}")
    )


def get_films(file_path: str = "data.json", film_id: int | None = None) -> list[dict] | dict:
    with open(file_path, "r", encoding="utf-8") as fp:
        films = json.load(fp)
        if film_id != None and film_id < len(films):
            return films[film_id]
        return films


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands([
        FILMS_COMMAND_BOT,
        START_COMMAND_BOT,
        CREATE_COMMAND_BOT
    ])
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
