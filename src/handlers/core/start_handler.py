from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, User, CallbackQuery, KeyboardButton, \
    ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from callbacks_data import PriceListCallback, TariffsCallback, EditFileCallback, \
    BackToMainMenuCallback, AlgorithmsCallback
from config import settings
from db.operations.users_operations import get_or_create_user


async def start_handler(
        call_or_message: CallbackQuery | Message,
        db_session: AsyncSession,
        state: FSMContext,
) -> None:
    await state.clear()

    user: User = call_or_message.from_user
    await get_or_create_user(user_id=user.id,
                             username=user.username,
                             db_session=db_session)

    buttons = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='⛏️Калькулятор доходности')],
                                            [KeyboardButton(text='👈 Главное меню')]
                                            ],
                                  resize_keyboard=True)
    await call_or_message.bot.send_message(
        chat_id=user.id,
        text="<b>Привет, на связи Crypto King Pro!</b>",
        reply_markup=buttons,
    )

    current_file_path = Path(__file__).resolve()
    filename = 'menu.txt'
    price_list_path = current_file_path.parent.parent.parent / 'texts' / filename

    with open(price_list_path, 'r', encoding='utf-8') as file:
        text = file.read()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Прайс лист",
                    callback_data=PriceListCallback().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚡️ Тарифы",
                    callback_data=TariffsCallback().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="⛏️ Калькулятор доходности",
                    callback_data=AlgorithmsCallback().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Сайт",
                    url='https://crypto-king.pro'
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Поддержка",
                    url=f"tg://user?id=286613674"
                )
            ],
        ]
    )
    if user.id in settings.ADMINS_ID:
        edit_button = InlineKeyboardButton(
            text="✏️ Редактировать",
            callback_data=EditFileCallback(filename=filename,
                                           back_callback=BackToMainMenuCallback().pack()).pack(),
        )
        keyboard.inline_keyboard.append(
            [edit_button]
        )
    await call_or_message.bot.send_message(
        chat_id=user.id,
        text=text,
        reply_markup=keyboard,
    )
