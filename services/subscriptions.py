import abc
import decimal

from pydantic import BaseModel

from enums import SubscriptionTypeEnum
from models.domain.instument import Instrument
from models.domain.subscription import Subscription
from repo.subscription import SubscriptionRepo
from services.uow import UoW


class SubscriptionMessage(BaseModel):
    user_chat_id: int
    message: str


class SubscriptionsService(abc.ABC):
    @abc.abstractmethod
    def get_messages_and_update(
        self, prices: list[tuple[Instrument, decimal.Decimal, decimal.Decimal]]
    ) -> list[SubscriptionMessage]:
        pass


class DefaultSubscriptionsService(SubscriptionsService):
    def __init__(self, uow: UoW, subscription_repo: SubscriptionRepo) -> None:
        self._uow = uow
        self._subscription_repo = subscription_repo

    def get_messages_and_update(
        self, prices: list[tuple[Instrument, decimal.Decimal, decimal.Decimal]]
    ) -> list[SubscriptionMessage]:
        result: list[SubscriptionMessage] = []
        for instrument, old_price, new_price in prices:
            if old_price is None:
                continue
            min_price = min(old_price, new_price)
            max_price = max(old_price, new_price)
            if min_price == max_price:
                continue
            subscriptions: list[Subscription] = self._subscription_repo.find_by(
                instrument_id=instrument.identity,
                price_gte=min_price,
                price_lt=max_price,
                is_active=True,
                crossing_disabled=False,
            )
            for sub in subscriptions:
                precision = sub.instrument_precision
                message_text = (
                    f"{instrument.ticker} price: {round(new_price, precision)}. "
                    f"Subscription to {round(sub.price, precision)}"
                )
                result.append(SubscriptionMessage(user_chat_id=sub.user_chat_id, message=message_text))
                if sub.type == SubscriptionTypeEnum.ONETIME:
                    self._subscription_repo.update_by(id_=sub.identity, update_data={"is_active": False})
                elif sub.type == SubscriptionTypeEnum.CROSSING:
                    self._subscription_repo.update_by(
                        is_active=True,
                        user_id=sub.user_id,
                        instrument_id=sub.instrument_id,
                        update_data={"crossing_disabled": False},
                    )
                    self._subscription_repo.update_by(
                        id_=sub.identity,
                        update_data={"crossing_disabled": True},
                    )
                    sub.crossing_disabled = True
            self._uow.commit()
        return result
