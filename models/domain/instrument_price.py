import decimal

from models.domain.base import BaseDomain
from models.domain.instument import Instrument


class InstrumentPrice(BaseDomain):
    instrument: Instrument
    price: decimal.Decimal
