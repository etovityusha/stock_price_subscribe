import decimal

from enums import SubscriptionTypeEnum
from models.domain.base import BaseDomain


class Subscription(BaseDomain):
    user_id: int
    user_chat_id: int
    instrument_id: int
    instrument_ticker: str
    instrument_precision: int
    price: decimal.Decimal
    type: SubscriptionTypeEnum
    crossing_disabled: bool
    is_active: bool
