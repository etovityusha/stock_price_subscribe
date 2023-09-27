import decimal

from enums import CommandTypeEnum, SubscriptionTypeEnum
from services.commands.dto import (
    CommandAddData,
    CommandDeleteAllData,
    CommandDeleteData,
    CommandMyData,
    CommandPriceData,
    CommandStepData,
)
from services.commands.parser.exceptions import (
    CommandNotFoundError,
    MoreThenOneCommandError,
    MoreThenOneSubTypeError,
    MoreThenOneTickerError,
    NotThreeDecimalError,
    TickerNotFoundError,
)
from services.commands.parser.interface import CommandParserService
from services.structures import OrderedSet


class DefaultCommandParserService(CommandParserService):
    """
    The DefaultCommandParserService class is an implementation of the CommandParserService interface.
    It provides methods to parse and extract command data from a given input.
    """

    def _get_command_my_data(self, data: OrderedSet) -> CommandMyData:
        return CommandMyData()

    def _get_command_delete_all_data(self, data: OrderedSet) -> CommandDeleteAllData:
        return CommandDeleteAllData()

    def _get_command_type(self, cmd: str) -> tuple[CommandTypeEnum, OrderedSet]:
        """
        method takes a string cmd as input and returns a tuple containing the CommandTypeEnum
        and an OrderedSet of message parts. It extracts the command type from the input and removes
        it from the message parts. If more than one command type is found, it raises a MoreThenOneCommandError.
        If no command type is found, it raises a CommandNotFoundError.
        """
        message_parts: OrderedSet[str] = OrderedSet(cmd.upper().split())
        user_command: CommandTypeEnum | None = None
        for command_type in CommandTypeEnum:
            if command_type.value in message_parts:
                if user_command is not None:
                    raise MoreThenOneCommandError
                message_parts.remove(command_type.value)
                user_command = command_type
        if user_command is None:
            raise CommandNotFoundError
        return user_command, message_parts

    def _get_command_add_data(self, data: OrderedSet) -> CommandAddData:
        """
        private method takes an OrderedSet data containing command parameters
        and returns a CommandAddData object. It extracts the subscription type, prices,
        and ticker from the data.
        """
        sub_type: SubscriptionTypeEnum | None = self._get_sub_type(data)
        prices: list[decimal.Decimal] = self._get_prices(data)
        ticker: str = self._get_ticker(data)
        return CommandAddData(
            ticker=ticker,
            prices=prices,
            type=sub_type,
        )

    def _get_command_step_data(self, data: OrderedSet) -> CommandStepData:
        """
        private method takes an OrderedSet data containing command parameters
        and returns a CommandStepData object. It extracts the subscription type, prices,
        and ticker from the data. If the number of prices is not 3, it raises a NotThreeDecimalError.
        """
        sub_type: SubscriptionTypeEnum | None = self._get_sub_type(data)
        prices: list[decimal.Decimal] = self._get_prices(data)
        if len(prices) != 3:  # from, to and step
            raise NotThreeDecimalError
        ticker: str = self._get_ticker(data)
        prices_iterator = iter(prices)
        return CommandStepData(
            ticker=ticker,
            type=sub_type,
            price_from=next(prices_iterator),
            price_to=next(prices_iterator),
            step=next(prices_iterator),
        )

    def _get_command_delete_data(self, data: OrderedSet) -> CommandDeleteData:
        """
        private method takes an OrderedSet data containing command parameters
        and returns a CommandDeleteData object. It extracts the prices and ticker from the data.
        If no prices are provided, it sets is_all to True
        """
        prices: list[decimal.Decimal] = self._get_prices(data)
        ticker: str = self._get_ticker(data)
        return CommandDeleteData(
            ticker=ticker,
            prices=prices,
            is_all=not bool(prices),
        )

    def _get_command_price_data(self, data: OrderedSet) -> CommandPriceData:
        """
        private method takes an OrderedSet data containing command parameters
        and returns a CommandPriceData object. It extracts the ticker from the data.
        """
        ticker = self._get_ticker(data)
        return CommandPriceData(ticker=ticker)

    def _get_prices(self, data: OrderedSet) -> list[decimal.Decimal]:
        """
        private method takes an OrderedSet data containing command parameters and
        returns an OrderedSet containing decimal prices. It removes non-decimal elements from the data
        """
        result, remove_elements = [], []
        for element in data:
            if isinstance(element, int | float | str) and not any(c.isalpha() for c in str(element)):
                decimal_price = decimal.Decimal(element)
                result.append(decimal_price)
                remove_elements.append(element)
        for el in remove_elements:
            data.remove(el)
        return result

    def _get_sub_type(self, data: OrderedSet) -> SubscriptionTypeEnum:
        """
        private method takes an OrderedSet data containing command parameters and
        returns the subscription type as SubscriptionTypeEnum if it exists in the data.
        If more than one subscription type is found, it raises a MoreThenOneSubTypeError.
        """
        picked: SubscriptionTypeEnum | None = None
        for st in SubscriptionTypeEnum:
            if st.value in data:
                data.remove(st.value)
                if picked is not None:
                    raise MoreThenOneSubTypeError
                picked = st
        if picked is None:
            picked = SubscriptionTypeEnum.get_default()
        return picked

    def _get_ticker(self, data: OrderedSet) -> str:
        """
        private method takes an OrderedSet data containing command parameters and
        returns the ticker as a string. If no ticker is found or multiple tickers are found,
        it raises the respective exceptions.
        """
        if not len(data):
            raise TickerNotFoundError
        if len(data) > 1:
            raise MoreThenOneTickerError(data)
        return data.first()
