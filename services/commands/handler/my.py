import abc
import decimal
from collections import defaultdict

from pydantic import BaseModel

from repo.subscription import SubscriptionRepo
from services.commands.dto import CommandMyData


class MyCommandResult(BaseModel):
    subscriptions: dict[str, list[decimal.Decimal]]


class MyCommandHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, user_id: int, data: CommandMyData) -> MyCommandResult:
        pass


class DefaultMyCommandHandler(MyCommandHandler):
    def __init__(
        self,
        subscription_repo: SubscriptionRepo,
    ) -> None:
        self._subscription_repo = subscription_repo

    def handle(self, user_id: int, data: CommandMyData) -> MyCommandResult:
        result = defaultdict(list)
        for row in self._subscription_repo.find_by(user_id=user_id, is_active=True):
            result[row.instrument_ticker].append(row.price)
        return MyCommandResult(subscriptions=result)
