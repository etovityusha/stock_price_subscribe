import abc

from models.domain.instument import Instrument
from repo.instrument import InstrumentRepo
from services.instrument_finder import InstrumentFinderService, InstrumentNotFoundError
from services.uow import UoW


class InstrumentService(abc.ABC):
    def get_or_create_by_ticker(self, ticker: str) -> Instrument:
        pass


class DefaultInstrumentService(InstrumentService):
    """
    DefaultInstrumentService

    Service class for managing instruments.

    Attributes:
        _uow (UoW): The unit of work for managing transactions.
        _instrument_repo (InstrumentRepo): The repository for instrument data.
        _finders (list[InstrumentFinderService]): List of instrument finder services.

    Methods:
        get_or_create_by_ticker(ticker: str) -> Instrument:
            Retrieves an instrument by ticker from the repository, or creates a new instrument
            by querying the instrument finder services.

    Raises:
        InstrumentNotFoundError: Raised if no instrument is found by any of the instrument finder services.
    """

    def __init__(
        self,
        finders: list[InstrumentFinderService],
        uow: UoW,
        instrument_repo: InstrumentRepo,
    ) -> None:
        self._uow = uow
        self._instrument_repo = instrument_repo
        self._finders = finders

    def get_or_create_by_ticker(self, ticker: str) -> Instrument:
        ticker = ticker.upper()
        instrument_from_db = self._instrument_repo.get_by_ticker(ticker=ticker)
        if instrument_from_db is not None:
            return instrument_from_db
        for finder in self._finders:
            try:
                obj = finder.find_instrument_info(ticker)
                self._instrument_repo.create(
                    ticker=ticker,
                    figi=obj.figi,
                    isin=obj.isin,
                    type_=obj.type,
                    precision=obj.precision,
                )
                self._uow.commit()
                return self._instrument_repo.get_by_ticker(ticker)
            except InstrumentNotFoundError:  # noqa: PERF203
                continue
        raise InstrumentNotFoundError
