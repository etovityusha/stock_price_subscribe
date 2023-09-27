from enums import InstrumentTypeEnum
from models.domain.base import BaseDomain


class Instrument(BaseDomain):
    ticker: str
    figi: str
    isin: str
    type: InstrumentTypeEnum
    precision: int
