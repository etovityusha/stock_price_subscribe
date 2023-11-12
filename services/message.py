import abc
import decimal
from typing import Generic, TypeVar

from enums import LocaleEnum
from services.commands.handler.delete import DeleteCommandResult
from services.commands.handler.my import MyCommandResult
from services.commands.handler.price import PriceCommandResult

L = TypeVar("L", bound=LocaleEnum)


class LocaleMessageBuilder(abc.ABC, Generic[L]):
    @abc.abstractmethod
    def welcome_new_user_msg(self) -> str:
        pass

    @abc.abstractmethod
    def welcome_old_user_msg(self) -> str:
        pass

    @abc.abstractmethod
    def help_msg(self) -> str:
        pass

    @abc.abstractmethod
    def parse_error_msg(self, owner_username: str) -> str:
        pass

    @abc.abstractmethod
    def delete_cmd_msg(self, data: DeleteCommandResult) -> str:
        pass

    @abc.abstractmethod
    def price_cmd_msg(self, data: PriceCommandResult) -> str:
        pass

    @abc.abstractmethod
    def my_cmd_msg(self, data: MyCommandResult) -> str:
        pass

    @classmethod
    def format_price(cls, price: decimal.Decimal, precision: int = 2) -> str:
        rounded_price = price.quantize(decimal.Decimal("1." + "0" * precision))
        return str(rounded_price)


class RuLocaleMessageBuilder(LocaleMessageBuilder[LocaleEnum.RU]):
    def welcome_new_user_msg(self) -> str:
        return "Добро пожаловать"

    def welcome_old_user_msg(self) -> str:
        return "С возвращением"

    def help_msg(self) -> str:
        return """
Примеры команд:

*ADD CROSSING GAZP 100 105*
добавить подписку на GAZP на цены 100 и 105, уведомления будут приходить при пересечении соседних уровней

*STEP ALWAYS GAZP 100 200 5*
добавить подписку на GAZP от 100 до 200 с шагом 5, уведомления будут приходить каждый раз

*DELETE GAZP 100*
удалить подписку на GAZP на цену 100

*DELETE GAZP*
удалить все подписки на GAZP

*DELETE_ALL*
удалить все мои подписки

*PRICE GAZP*
получить текущую цену GAZP

*MY*
список моих подписок

*/help*
получить справку о командах
    """

    def parse_error_msg(self, owner_username: str) -> str:
        return f"Ошибка. Свяжитесь с [владельцем бота](https://t.me/{owner_username})"

    def delete_cmd_msg(self, data: DeleteCommandResult) -> str:
        return f"Удалено {data.deleted_count} подписок"

    def price_cmd_msg(self, data: PriceCommandResult) -> str:
        return f"Цена {data.ticker} = {self.format_price(data.price, data.precision)}"

    def my_cmd_msg(self, data: MyCommandResult) -> str:
        if not data.subscriptions:
            return "У вас нет активных подписок"
        return "\n".join(
            f"{ticker}: {', '.join(self.format_price(p) for p in prices)}"
            for ticker, prices in data.subscriptions.items()
        )


class EnLocaleMessageBuilder(LocaleMessageBuilder[LocaleEnum.EN]):
    def welcome_new_user_msg(self) -> str:
        return "Welcome"

    def welcome_old_user_msg(self) -> str:
        return "Welcome back"

    def help_msg(self) -> str:
        return """
Command examples:

*ADD CROSSING GAZP 100 105*
add subscription for GAZP at prices 100 and 105, notifications will come when crossing adjacent levels

*STEP ALWAYS GAZP 100 200 5*
add a subscription for GAZP from 100 to 200 with a step of 5, notifications will come each time

*DELETE GAZP 100*
remove a subscription for GAZP at a price of 100

*DELETE GAZP*
remove all subscriptions for GAZP

*DELETE_ALL*
remove all my subscriptions

*PRICE GAZP*
get the current price for GAZP

*MY*
list of my subscriptions

*/help*
get command help
        """

    def parse_error_msg(self, owner_username: str) -> str:
        return f"Error. Contact the [bot owner](https://t.me/{owner_username})"

    def delete_cmd_msg(self, data: DeleteCommandResult) -> str:
        return f"Removed {data.deleted_count} subscriptions"

    def price_cmd_msg(self, data: PriceCommandResult) -> str:
        return f"Price {data.ticker} = {self.format_price(data.price, data.precision)}"

    def my_cmd_msg(self, data: MyCommandResult) -> str:
        if not data.subscriptions:
            return "You have no active subscriptions"
        return "\n".join(
            f"{ticker}: {', '.join(self.format_price(p) for p in prices)}"
            for ticker, prices in data.subscriptions.items()
        )


def get_locale_msg_builder(locale: LocaleEnum) -> LocaleMessageBuilder:
    if locale == LocaleEnum.RU:
        return RuLocaleMessageBuilder()
    return EnLocaleMessageBuilder()
