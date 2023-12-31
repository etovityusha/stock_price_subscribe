import abc
import decimal

from pydantic import BaseModel

from enums import SubscriptionTypeEnum
from models.domain.instument import Instrument
from models.domain.subscription import Subscription
from repo.subscription import SubscriptionRepo
from repo.user import UserRepo
from services.message import get_locale_msg_builder
from services.price_updater import UpdatedPriceResult
from services.uow import UoW


class SubscriptionMessage(BaseModel):
    user_chat_id: int
    message: str


class SubscriptionsService(abc.ABC):
    @abc.abstractmethod
    def get_messages_and_update(self, prices: list[UpdatedPriceResult]) -> list[SubscriptionMessage]:
        pass


class DefaultSubscriptionsService(SubscriptionsService):
    def __init__(self, uow: UoW, subscription_repo: SubscriptionRepo, user_repo: UserRepo) -> None:
        self._uow = uow
        self._subscription_repo = subscription_repo
        self._user_repo = user_repo

    def get_messages_and_update(self, prices: list[UpdatedPriceResult]) -> list[SubscriptionMessage]:
        result: list[SubscriptionMessage] = []
        for row in prices:
            if row.old_price is None:
                continue

            min_price = min(row.old_price, row.new_price)
            max_price = max(row.old_price, row.new_price)
            if min_price == max_price:
                continue
            subscriptions: list[Subscription] = self._subscription_repo.find_by(
                instrument_id=row.instrument.identity,
                price_gte=min_price,
                price_lt=max_price,
                is_active=True,
                crossing_disabled=False,
            )
            for sub in subscriptions:
                msg_text = get_locale_msg_builder(sub.user_locale).sub_msg(
                    instrument_ticker=sub.instrument_ticker,
                    instrument_precision=sub.instrument_precision,
                    sub_price=sub.price,
                    old_price=row.old_price,
                    current_price=row.new_price,
                )
                result.append(SubscriptionMessage(user_chat_id=sub.user_chat_id, message=msg_text))
                if sub.type == SubscriptionTypeEnum.ONETIME:
                    self._subscription_repo.update_by(id_=sub.identity, update_data={"is_active": False})
                elif sub.type == SubscriptionTypeEnum.CROSSING:
                    self._subscription_repo.update_by(
                        is_active=True,
                        user_id=sub.user_id,
                        instrument_id=sub.instrument_id,
                        type_=SubscriptionTypeEnum.CROSSING,
                        update_data={"crossing_disabled": False},
                    )
                    self._subscription_repo.update_by(
                        id_=sub.identity,
                        update_data={"crossing_disabled": True},
                    )
        self._uow.commit()
        return result
