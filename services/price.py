import abc
import decimal
from typing import Iterable

import requests

from models.domain.instument import Instrument
from repo.instrument_price import InstrumentPriceRepo
from services.uow import UoW


class PriceUpdaterService(abc.ABC):
    @abc.abstractmethod
    def update_instruments_prices(
        self, instruments: Iterable[Instrument]
    ) -> list[tuple[Instrument, decimal.Decimal, decimal.Decimal | None]]:
        pass


class TinkoffPriceUpdaterService(PriceUpdaterService):
    def __init__(self, token: str, uow: UoW, instrument_prices_repo: InstrumentPriceRepo):
        self._token = token
        self._base_url = "https://invest-public-api.tinkoff.ru/rest/"
        self._headers = {"Authorization": f"Bearer {token}"}
        self._uow = uow
        self._instrument_prices_repo = instrument_prices_repo

    def update_instruments_prices(
        self, instruments: Iterable[Instrument]
    ) -> list[tuple[Instrument, decimal.Decimal, decimal.Decimal | None]]:
        data = requests.post(
            self._base_url + "tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices",
            headers=self._headers,
            json={"figi": [instrument.figi for instrument in instruments]},
        ).json()
        prices: list[decimal.Decimal | None] = [
            decimal.Decimal(f"{row['price']['units']}.{str(row['price']['nano']).zfill(9)}") if "price" in row else None
            for row in data["lastPrices"]
        ]
        result = []
        for instrument, price in zip(instruments, prices):
            if price is None:
                continue
            old_price = self._instrument_prices_repo.create_or_update(instrument_id=instrument.identity, price=price)
            result.append((instrument, old_price, price))
        self._uow.commit()
        return result
