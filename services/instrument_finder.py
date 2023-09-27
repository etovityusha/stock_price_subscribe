import abc
import datetime

import requests
from cachetools.func import ttl_cache

from enums import InstrumentTypeEnum
from models.domain.instument import Instrument


class InstrumentNotFoundError(Exception):
    pass


class InstrumentFinderService(abc.ABC):
    @abc.abstractmethod
    def find_instrument_info(self, ticker: str) -> Instrument:
        pass


class TinkoffInstrumentFinderService(InstrumentFinderService):
    """
    Implementation of the InstrumentFinderService that retrieves instrument information from the Tinkoff API.

    Args:
        token (str): The authentication token used to access the Tinkoff API.

    Attributes:
        _headers (dict): The headers containing the authentication token.
        _base_url (str): The base URL of the Tinkoff API.

    """

    CONST_CANDLE_INTERVAL = "CANDLE_INTERVAL_4_HOUR"
    CANDLE_PRICE_NAMES = ("open", "high", "low", "close")

    def __init__(self, token: str):
        self._headers = {"Authorization": f"Bearer {token}"}
        self._base_url = "https://invest-public-api.tinkoff.ru/rest/"

    def find_instrument_info(self, ticker: str) -> Instrument:
        data = requests.post(
            self._base_url + "tinkoff.public.invest.api.contract.v1.InstrumentsService/FindInstrument",
            headers=self._headers,
            json={
                "query": ticker,
                "instrumentKind": "INSTRUMENT_TYPE_UNSPECIFIED",
                "apiTradeAvailableFlag": True,
            },
        ).json()

        instruments = data["instruments"]
        if len(instruments) == 0:
            raise InstrumentNotFoundError

        for row in instruments:
            if row["ticker"].upper() == ticker:
                return Instrument(
                    ticker=ticker,
                    figi=row["figi"],
                    isin=row["isin"],
                    type=InstrumentTypeEnum(row["instrumentType"].upper()),
                    precision=self._get_precision(row["uid"]),
                )
        raise InstrumentNotFoundError

    def _get_precision(self, tinkoff_uid: str) -> int:
        today_str, week_ago_str = self._get_dates()
        data = requests.post(
            url=self._base_url + "tinkoff.public.invest.api.contract.v1.MarketDataService/GetCandles",
            headers=self._headers,
            json={
                "instrumentId": tinkoff_uid,
                "interval": self.CONST_CANDLE_INTERVAL,
                "from": week_ago_str,
                "to": today_str,
            },
        ).json()
        max_precision = 0
        for candle in data["candles"]:
            for price_name in self.CANDLE_PRICE_NAMES:
                price = candle.get(price_name, {}).get("nano", 0)
                price_transformed = price / 1e9
                precision = len(str(price_transformed).split(".")[1])
                max_precision = max(max_precision, precision)
        return max_precision

    @ttl_cache(ttl=600)
    def _get_dates(self) -> tuple[str, str]:
        now = datetime.datetime.now(datetime.timezone.utc)
        now_str = now.strftime("%Y-%m-%dT00:00:00Z")
        week_ago = now - datetime.timedelta(weeks=1)
        week_ago_str = week_ago.strftime("%Y-%m-%dT00:00:00Z")
        return now_str, week_ago_str
