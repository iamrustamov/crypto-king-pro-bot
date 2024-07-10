from aiogram import Router, F
from aiogram.filters import Command

from callbacks_data import BackToMainMenuCallback, PriceListCallback, EditFileCallback, TariffsCallback
from states import TextEdit


def register_core_handlers() -> Router:
    from .start_handler import start_handler
    from .price_list_handler import price_list_handler
    from .edit_file_handler import edit_file_handler, write_new_text_handler
    from .tariffs_handler import tariffs_handler

    router = Router()

    router.message.register(start_handler, Command("start", ignore_case=True))
    router.callback_query.register(start_handler, BackToMainMenuCallback.filter())
    router.callback_query.register(tariffs_handler, TariffsCallback.filter())
    router.callback_query.register(price_list_handler, PriceListCallback.filter())
    router.callback_query.register(edit_file_handler, EditFileCallback.filter())
    router.message.register(write_new_text_handler, TextEdit.new_text)

    return router
