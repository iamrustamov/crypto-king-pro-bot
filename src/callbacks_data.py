from aiogram.filters.callback_data import CallbackData

__all__ = ["PriceListCallback",
           "TariffsCallback",
           "YieldCalculatorCallback",
           "BackToMainMenuCallback",
           "EditFileCallback"]


class PriceListCallback(CallbackData, prefix="price-list"):
    pass


class TariffsCallback(CallbackData, prefix="tariffs"):
    pass


class YieldCalculatorCallback(CallbackData, prefix="yield-calculator"):
    pass


class BackToMainMenuCallback(CallbackData, prefix="back-to-main-menu"):
    pass


class EditFileCallback(CallbackData, prefix="edit-file"):
    filename: str
    back_callback: str
