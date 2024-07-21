from pathlib import Path

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, User, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from callbacks_data import PriceListCallback, TariffsCallback, EditFileCallback, \
    BackToMainMenuCallback, AlgorithmsCallback
from config import settings
from db.operations.users_operations import get_or_create_user

import requests
import random
from bs4 import BeautifulSoup


def get_free_proxies():
    r = requests.get('https://free-proxy-list.net')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')

    proxies = []
    for row in table:
        if row.find_all('td')[4].text == 'elite proxy':
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
    return proxies


def get_session(proxies):
    # создать HTTP‑сеанс
    session = requests.Session()
    # выбираем один случайный прокси
    proxy = random.choice(proxies)
    session.proxies = {"http": "45.152.116.208:63998:6tC7WB9E:mPs6ENPM", "https": "45.152.116.208:63998:6tC7WB9E:mPs6ENPM"}
    return session


import requests
import requests.auth

class HTTPProxyDigestAuth(requests.auth.HTTPDigestAuth):
    def handle_407(self, r):
        """Takes the given response and tries digest-auth, if needed."""

        num_407_calls = r.request.hooks['response'].count(self.handle_407)

        s_auth = r.headers.get('Proxy-authenticate', '')

        if 'digest' in s_auth.lower() and num_407_calls < 2:

            self.chal = requests.auth.parse_dict_header(s_auth.replace('Digest ', ''))

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.raw.release_conn()

            r.request.headers['Authorization'] = self.build_digest_header(r.request.method, r.request.url)
            r.request.send(anyway=True)
            _r = r.request.response
            _r.history.append(r)

            return _r

        return r

    def __call__(self, r):
        if self.last_nonce:
            r.headers['Proxy-Authorization'] = self.build_digest_header(r.method, r.url)
        r.register_hook('response', self.handle_407)
        return r

async def start_handler(
        call_or_message: CallbackQuery | Message,
        db_session: AsyncSession,
        state: FSMContext,
) -> None:
    user: User = call_or_message.from_user

    session = requests.Session()
    # выбираем один случайный прокси
    # proxies = {
    #     'http': 'http://user:pass@45.152.116.208:63999',
    #     'https': 'https://user:pass@45.152.116.208:63999'
    # }

    proxies = {
        'http': 'socks5://6tC7WB9E:mPs6ENPM@45.152.116.208:63999',
        'https': 'socks5://6tC7WB9E:mPs6ENPM@45.152.116.208:63999'
    }

    try:
        await call_or_message.bot.send_message(chat_id=user.id,
                                          text="Страница запроса с IP:" + requests.get("https://whattomine.com/asic.json?hh=true&factor[hh_hr]=10&factor[cost_currency]=USD&sort=Profit24&volume=0&revenue=24h&exchanges=binance,bitfinex,coinex,exmo,gate,graviex,hitbtc,ogre,poloniex,xeggex&dataset=Main", timeout=1.5, proxies=proxies).text.strip())
    except Exception as e:
        print(e)

    return

    await state.clear()

    user: User = call_or_message.from_user
    await get_or_create_user(user_id=user.id,
                             username=user.username,
                             db_session=db_session)
    current_file_path = Path(__file__).resolve()
    filename = 'menu.txt'
    price_list_path = current_file_path.parent.parent.parent / 'texts' / filename

    with open(price_list_path, 'r', encoding='utf-8') as file:
        text = file.read()
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
                    callback_data=AlgorithmsCallback().pack(),
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
    if user.id in settings.ADMINS_ID:
        edit_button = InlineKeyboardButton(
            text="Редактировать ✏️",
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
