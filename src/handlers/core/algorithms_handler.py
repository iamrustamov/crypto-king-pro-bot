import json
from pathlib import Path

import requests
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, User, FSInputFile

from callbacks_data import BackToMainMenuCallback, CalculateAlgorithmCallback, \
    AlgorithmsCallback
from states import PowerInput
from utils.pdf_generator import pdf_generator


def mh_to_gh(mh):
    # Преобразование MH/s в GH/s
    gh = mh / 1000.0

    # Форматирование до одной десятичной цифры
    formatted_gh = f"{gh:.1f}"

    return formatted_gh



async def algorithms_handler(
        call_or_message: CallbackQuery | Message,
        state: FSMContext,
) -> None:
    await state.clear()

    current_file_path = Path(__file__).resolve()
    filename = 'algorithms.json'
    price_list_path = current_file_path.parent.parent.parent / 'texts' / filename

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    with open(price_list_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    for algorithm in data.keys():
        button = InlineKeyboardButton(
            text=algorithm,
            callback_data=CalculateAlgorithmCallback(name=algorithm).pack(),
        )
        keyboard.inline_keyboard.append(
            [button]
        )
    button = InlineKeyboardButton(
        text="‹ Назад",
        callback_data=BackToMainMenuCallback().pack(),
    )
    keyboard.inline_keyboard.append(
        [button]
    )

    await call_or_message.bot.send_message(
        chat_id=call_or_message.from_user.id,
        text="Выберите алгоритм:",
        reply_markup=keyboard,
    )


async def calculate_algorithm_handler(
        call: CallbackQuery,
        callback_data: CalculateAlgorithmCallback,
        state: FSMContext,
) -> None:
    """

    """
    await state.clear()

    current_file_path = Path(__file__).resolve()
    filename = "algorithms.json"
    filepath = current_file_path.parent.parent.parent / 'texts' / filename

    algorithm_name = callback_data.name
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    algorithm = data[algorithm_name]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚫 Отменить",
                    callback_data=AlgorithmsCallback().pack(),
                )
            ],
        ]
    )

    msg = await call.bot.send_message(
        chat_id=call.from_user.id,
        text=f"⚙️Введите мощность {algorithm.get('hash_type')}:",
        reply_markup=keyboard,
    )
    await state.set_data({'algorithm_name': callback_data.name,
                          'previous_messages_id': [msg.message_id]})
    await state.set_state(PowerInput.power)


async def input_power_handler(
        message: Message,
        state: FSMContext,
) -> None:
    user: User = message.from_user
    user_data = await state.get_data()
    await message.bot.send_message(chat_id=user.id,
                                   text="♻ Получение данных... Пожалуйста, подождите.")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="‹ Назад",
                    callback_data=AlgorithmsCallback().pack(),
                )
            ],
        ]
    )
    try:
        number = float(message.text)
        if number < 0:
            msg = await message.bot.send_message(chat_id=user.id,
                                                 text="⚠️ Введите положительное число:",
                                                 reply_markup=keyboard)
            await state.update_data({'previous_messages_id': [msg.message_id]})
            return
    except ValueError:
        msg = await message.bot.send_message(chat_id=user.id,
                                             text="⚠️ Введите число:",
                                             reply_markup=keyboard)

        await state.update_data({'previous_messages_id': [msg.message_id]})
        return

    await state.clear()
    current_file_path = Path(__file__).resolve()
    filename = "algorithms.json"
    filepath = current_file_path.parent.parent.parent / 'texts' / filename

    algorithm_name = user_data.get("algorithm_name")
    with open(filepath, 'r', encoding='utf-8') as file:
        algorithm_data = json.load(file)
    algorithm = algorithm_data[algorithm_name]
    proxies = {
        'http': 'socks5://6tC7WB9E:mPs6ENPM@45.152.116.208:63999',
        'https': 'socks5://6tC7WB9E:mPs6ENPM@45.152.116.208:63999'
    }
    url = algorithm.get("url")
    url = url.format(hashrate=message.text)
    response = requests.get(url, timeout=3, proxies=proxies)
    response.raise_for_status()
    if response.status_code == 200:
        resp_data = response.json()
    else:
        print("Не удалось получить данные, статус-код:", response.status_code)
        await message.bot.send_message(chat_id=user.id,
                                       text="👾 Не удалось сформировать отчет")
        return
    if algorithm_name == 'Scrypt':
        message.text = mh_to_gh(message.text)

    if algorithm_name == 'SHA-256':
        filename = await pdf_generator(data=resp_data, btc_exchange_rate=resp_data['coins']['Bitcoin']['exchange_rate'],
                                       user_id=user.id, algo_name=algorithm_name, hashrate=message.text,
                                       hash_type=algorithm['hash_type'])
    else:
        sha_256_url = algorithm_data['SHA-256'].get("url")
        response = requests.get(sha_256_url, timeout=3, proxies=proxies)
        response.raise_for_status()
        if response.status_code == 200:
            sha_256_data = response.json()
        else:
            print("Не удалось получить данные, статус-код:", response.status_code)
            await message.bot.send_message(chat_id=user.id,
                                           text="👾 Не удалось сформировать отчет")
            return
        filename = await pdf_generator(data=resp_data,
                                       btc_exchange_rate=sha_256_data['coins']['Bitcoin']['exchange_rate24'],
                                       user_id=user.id, algo_name=algorithm_name, hashrate=message.text,
                                       hash_type=algorithm['hash_type'])

    await message.bot.send_document(
        chat_id=user.id,
        document=FSInputFile(filename, filename="report.pdf"),
        caption=f"{algorithm_name} {message.text} {algorithm['hash_type']}",
    )
    filename.unlink(missing_ok=True)
