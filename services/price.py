import abc
import datetime
import decimal
from typing import Iterable

from pydantic import BaseModel

import requests

from models.domain.instument import Instrument


class InstrumentPriceResult(BaseModel):
    instrument: Instrument
    new_price: decimal.Decimal


class PriceService(abc.ABC):
    @abc.abstractmethod
    def get_prices(self, instruments: Iterable[Instrument]) -> InstrumentPriceResult:
        pass

    @classmethod
    @abc.abstractmethod
    def from_utc_time(cls) -> datetime.time:
        pass

    @classmethod
    @abc.abstractmethod
    def to_utc_time(cls) -> datetime.time:
        pass

    @classmethod
    @abc.abstractmethod
    def weekdays(cls) -> set[int]:
        pass


class TinkoffPriceService(PriceService):
    @classmethod
    def from_utc_time(cls) -> datetime.time:
        return datetime.time(7)

    @classmethod
    def to_utc_time(cls) -> datetime.time:
        return datetime.time(16)

    @classmethod
    def weekdays(cls) -> set[int]:
        return {0, 1, 2, 3, 4}

    def __init__(self, token: str) -> None:
        self._token = token
        self._base_url = "https://invest-public-api.tinkoff.ru/rest/"
        self._headers = {"Authorization": f"Bearer {token}"}

    def get_prices(self, instruments: Iterable[Instrument]) -> list[InstrumentPriceResult]:
        data = requests.post(
            self._base_url + "tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices",
            headers=self._headers,
            json={"figi": [instrument.figi for instrument in instruments]},
        ).json()
        prices: list[decimal.Decimal | None] = [
            decimal.Decimal(f"{row['price']['units']}.{str(row['price']['nano']).zfill(9)}") if "price" in row else None
            for row in data["lastPrices"]
        ]
        return [
            InstrumentPriceResult(instrument=instrument, new_price=price)
            for instrument, price in zip(instruments, prices)
            if price is not None
        ]
