from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

FILMS_COMMAND = Command("films")
FILMS_CREATE = Command("add_film")

FILMS_COMMAND_BOT = BotCommand(command="films", description="Перегляд списку фільмів")
START_COMMAND_BOT = BotCommand(command="start", description="Почати розмову")
CREATE_COMMAND_BOT = BotCommand(command="add_film", description="Додати фільм")
