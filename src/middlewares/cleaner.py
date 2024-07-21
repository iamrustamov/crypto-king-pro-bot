from typing import Callable, Any, Awaitable

from aiogram import Bot, BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Update, Message

__all__ = ["CleanerMiddleware"]


class CleanerMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Awaitable[Any] | None:
        await self._on_process_message(event, data)
        result = await handler(event, data)
        return result

    async def _on_process_message(self, msg: Message, data: dict):
        state: FSMContext = data.get("state")
        if state:
            state_data = await state.get_data()
            previous_messages_id = state_data.get("previous_messages_id")
            if previous_messages_id:
                for message_id in previous_messages_id:
                    # noinspection PyBroadException
                    try:
                        await msg.bot.edit_message_reply_markup(
                            chat_id=msg.chat.id, message_id=message_id
                        )
                    except Exception as e:
                        ...
                    print(f"Удалили кнопку у сообщения #{message_id}")
                state_data.pop("previous_messages_id")
                await state.set_data(state_data)