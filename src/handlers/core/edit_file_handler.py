from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User, CallbackQuery, Message

from callbacks_data import EditFileCallback
from states import TextEdit


async def edit_file_handler(
        call: CallbackQuery,
        callback_data: EditFileCallback,
        state: FSMContext
):
    await state.clear()
    user: User = call.from_user

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚫 Отмена",
                    callback_data=callback_data.back_callback
                )
            ]
        ]
    )
    await call.bot.send_message(
        chat_id=user.id,
        text="Напишите новый текст:",
        reply_markup=keyboard,
    )
    await state.set_data({'filename': callback_data.filename,
                          'back_callback': callback_data.back_callback})
    await state.set_state(TextEdit.new_text)


async def write_new_text_handler(
        message: Message, state: FSMContext
):
    user: User = message.from_user
    user_data = await state.get_data()
    await state.clear()
    current_file_path = Path(__file__).resolve()
    filename = user_data.get("filename")
    filepath = current_file_path.parent.parent.parent / 'texts' / filename

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(message.text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆗",
                    callback_data=user_data.get('back_callback')
                )
            ]
        ]
    )
    await message.bot.send_message(
        chat_id=user.id,
        text="Вы успешно сменили текст",
        reply_markup=keyboard,
    )
