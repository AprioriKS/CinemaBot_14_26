import asyncio
import logging
import sys
import json

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, URLInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import BOT_TOKEN as TOKEN
from config import USER_ADMIN
from commands import (FILMS_COMMAND,
                      FILMS_CREATE,
                      FILMS_COMMAND_BOT,
                      START_COMMAND_BOT,
                      CREATE_COMMAND_BOT,
                      )
from keyboards import films_keyboard_markup, FilmCallback
from model import Film
from state import FilmForm

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


@dp.message(FILMS_CREATE)
async def films_create(message: Message, state: FSMContext) -> None:
    if message.from_user.id == USER_ADMIN:
        await state.set_state(FilmForm.name)
        await message.answer(f"Введіть назву фільму", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Доступно тільки адміну", reply_markup=ReplyKeyboardRemove())


@dp.message(FilmForm.name)
async def films_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(f"Введіть опис фільму", reply_markup=ReplyKeyboardRemove())


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(
        f"Вкажіть рейтинг фільму від 0 до 10.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.rating)


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=message.text)
    await message.answer(
        f"Введіть жанр фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.genre)


@dp.message(FilmForm.genre)
async def films_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await message.answer(
        text=f"Введіть акторів фільму через роздільник ', '\n"
             + html.bold("Обов'язкова кома та відступ після неї."),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.actors)


@dp.message(FilmForm.actors)
async def films_actors(message: Message, state: FSMContext) -> None:
    await state.update_data(actors=message.text.split(", "))
    await message.answer(
        f"Введіть посилання на постер фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(FilmForm.poster)



@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
    data = await state.update_data(poster=message.text)
    film_data = Film(**data)
    print(film_data)
    print(film_data.model_dump())
    add_film(film_data.model_dump())
    await state.clear()
    await message.answer(
        f"Фільм {film_data.name} успішно додано.",
        reply_markup=ReplyKeyboardRemove(),
    )

def add_film(film: dict, file_path: str = "data.json"):
    films = get_films(file_path=file_path, film_id=None)
    if films:
        films.append(film)
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(
                films,
                fp,
                indent=4,
                ensure_ascii=False
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
