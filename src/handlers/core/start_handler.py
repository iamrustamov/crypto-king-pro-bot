from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, User
from sqlalchemy.ext.asyncio import AsyncSession

from callbacks_data import PriceListCallback, TariffsCallback, YieldCalculatorCallback
from db.operations.users_operations import get_or_create_user


async def start_handler(
        message: Message, db_session: AsyncSession
):
    user: User = message.from_user
    await get_or_create_user(user_id=user.id,
                             username=user.username,
                             db_session=db_session)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Прайс лист 📄",
                    callback_data=PriceListCallback().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Тарифы ⚡️",
                    callback_data=TariffsCallback().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Калькулятор доходности ⛏️",
                    callback_data=YieldCalculatorCallback().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Сайт 🌐",
                    url='https://youtu.be/ltzyroknKDk'
                )
            ],
            [
                InlineKeyboardButton(
                    text="Поддержка 💬",
                    url=f"tg://user?id=286613674"
                )
            ],
        ]
    )
    await message.bot.send_message(
        chat_id=user.id,
        text="<b>Привет, на связи Crypto King Pro!</b>\n\n"
             "Наши контакты:\n"
             "7 (495) XXX-XX-XX info@some.domain",
        reply_markup=keyboard,
    )
