import logging

from pydantic import BaseModel
import abc
import decimal

from models.domain.instrument_price import InstrumentPrice
from models.domain.instument import Instrument
from repo.instrument_price import InstrumentPriceRepo
from services.price import InstrumentPriceResult
from services.uow import UoW

logger = logging.getLogger(__name__)


class UpdatedPriceResult(BaseModel):
    instrument: Instrument
    old_price: decimal.Decimal | None
    new_price: decimal.Decimal


class PriceUpdaterService(abc.ABC):
    @abc.abstractmethod
    def update_prices(self, data: list[InstrumentPriceResult]) -> list[UpdatedPriceResult]:
        pass


class PriceUpdaterServiceImpl(PriceUpdaterService):
    def __init__(self, uow: UoW, instrument_prices_repo: InstrumentPriceRepo):
        self.uow = uow
        self.instrument_prices_repo = instrument_prices_repo

    def update_prices(self, data: list[InstrumentPriceResult]) -> list[UpdatedPriceResult]:
        logger.info("Starting the price update process.")
        instrument_ids = [row.instrument.identity for row in data]
        current_prices: list[InstrumentPrice] = self.instrument_prices_repo.find_by(instrument_id_in=instrument_ids)
        logger.info("Fetched current prices from the repository.")
        current_prices_map: dict[int, decimal.Decimal] = {ip.instrument.identity: ip.price for ip in current_prices}

        for row in data:
            self.instrument_prices_repo.create_or_update(instrument_id=row.instrument.identity, price=row.new_price)

        updated_prices = [
            UpdatedPriceResult(
                instrument=row.instrument,
                new_price=row.new_price,
                old_price=current_prices_map.get(row.instrument.identity),
            )
            for row in data
        ]
        logger.info("Price update process completed successfully.")

        return updated_prices
