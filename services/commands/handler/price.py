import abc
import decimal

from pydantic import BaseModel

from repo.instrument import InstrumentRepo
from repo.instrument_price import InstrumentPriceRepo
from services.commands.dto import CommandPriceData


class PriceCommandResult(BaseModel):
    ticker: str
    price: decimal.Decimal


class PriceCommandHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, user_id: int, data: CommandPriceData) -> PriceCommandResult:
        pass


class DefaultPriceCommandHandler(PriceCommandHandler):
    def __init__(
        self,
        instrument_repo: InstrumentRepo,
        instrument_price_repo: InstrumentPriceRepo,
    ) -> None:
        self._instrument_repo = instrument_repo
        self._instrument_price_repo = instrument_price_repo

    def handle(self, user_id: int, data: CommandPriceData) -> PriceCommandResult:
        instrument = self._instrument_repo.get_by_ticker(data.ticker)
        instrument_price = self._instrument_price_repo.get_by_instrument_id(instrument_id=instrument.identity)
        return PriceCommandResult(ticker=instrument_price.instrument.ticker, price=instrument_price.price)
