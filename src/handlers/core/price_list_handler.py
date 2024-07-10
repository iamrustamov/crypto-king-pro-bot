from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import settings

from callbacks_data import BackToMainMenuCallback, EditFileCallback, PriceListCallback


async def price_list_handler(
    message: Message,
    state: FSMContext,
) -> None:
    await state.clear()

    current_file_path = Path(__file__).resolve()
    filename = 'price_list.txt'
    price_list_path = current_file_path.parent.parent.parent / 'texts' / filename

    with open(price_list_path, 'r', encoding='utf-8') as file:
        text = file.read()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=BackToMainMenuCallback().pack(),
                )
            ],
        ]
    )
    if message.from_user.id in settings.ADMINS_ID:
        edit_button = InlineKeyboardButton(
            text="Редактировать ✏️",
            callback_data=EditFileCallback(filename=filename,
                                           back_callback=PriceListCallback().pack()).pack(),
        )
        keyboard.inline_keyboard.append(
            [edit_button]
        )
    await message.bot.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=keyboard,
        )