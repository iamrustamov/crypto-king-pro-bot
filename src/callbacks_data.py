from aiogram.filters.callback_data import CallbackData

__all__ = ["PriceListCallback",
           "TariffsCallback",
           "AlgorithmsCallback",
           "BackToMainMenuCallback",
           "CalculateAlgorithmCallback",
           "EditFileCallback"]


class PriceListCallback(CallbackData, prefix="price-list"):
    pass


class TariffsCallback(CallbackData, prefix="tariffs"):
    pass


class AlgorithmsCallback(CallbackData, prefix="algorithms"):
    pass


class CalculateAlgorithmCallback(CallbackData, prefix="calc-algo"):
    name: str


class BackToMainMenuCallback(CallbackData, prefix="back-to-main-menu"):
    pass


class EditFileCallback(CallbackData, prefix="edit-file"):
    filename: str
    back_callback: str
