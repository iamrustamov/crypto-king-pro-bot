import logging
from enum import Enum

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


class CommandName(Enum):
    """Enumeration of bot command names.

    This enumeration defines the available command names as string constants.
    """

    START: str = "start"


async def bot_commands(bot: Bot) -> bool:
    """Set custom bot commands.

    This function sets custom bot commands along with their descriptions using the
    provided Bot instance.

    :param bot: The Bot instance to set custom commands for.
    :return: bool:
    """
    commands = [
        (
            [
                BotCommand(
                    command=CommandName.START.value, description="Запустить бота"
                ),
            ],
            BotCommandScopeAllPrivateChats(),
            "ru",
        )
    ]
    for commands_list, commands_scope, language in commands:
        await bot.set_my_commands(
            commands=commands_list, scope=commands_scope, language_code=language
        )
    logging.info("Базовые команды успешно установлены")
