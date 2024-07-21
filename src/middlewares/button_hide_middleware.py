import os
from typing import Callable, Any, Awaitable

from aiogram import Bot, BaseMiddleware
from aiogram.types import CallbackQuery, ContentType, Update

__all__ = ["ButtonHideMiddleware"]


class ButtonHideMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Awaitable[Any] | None:
        await self._on_process_callback_query(event)
        result = await handler(event, data)
        await self._on_post_process_callback_query(event, result, data)
        return result

    async def _on_process_callback_query(self, callback: CallbackQuery):
        if os.environ.get("DEBUG"):
            pass
        else:
            try:
                for row in callback.message.reply_markup.inline_keyboard:
                    for button in row:
                        if button.callback_data == callback.data:
                            if callback.message.content_type == ContentType.TEXT:
                                if button.text == "SHA-256":
                                    await callback.message.edit_text(
                                        f"{callback.message.text}\n\n› SHA-256",
                                    )
                                else:
                                    await callback.message.edit_text(
                                        f"{callback.message.text}\n\n› {button.text.replace('›', '').replace('‹', '').strip()}️",
                                    )
                            else:
                                await callback.message.edit_caption(
                                    callback.message.caption
                                    + f"\n\n› {button.replace('›', '').replace('‹', '').strip()}️",
                                )
                            return
            except Exception as e:
                print(e)

    async def _on_post_process_callback_query(
        self, callback: CallbackQuery, results, data: dict
    ):
        try:
            await callback.answer()
        except Exception as e:
            pass
