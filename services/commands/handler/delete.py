import abc

from pydantic import BaseModel

from repo.subscription import SubscriptionRepo
from services.commands.dto import CommandDeleteData
from services.instrument import InstrumentService
from services.uow import UoW


class DeleteCommandResult(BaseModel):
    deleted_count: int | None


class DeleteCommandHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, user_id: int, data: CommandDeleteData) -> DeleteCommandResult:
        pass


class DefaultDeleteCommandHandler(DeleteCommandHandler):
    def __init__(
        self,
        instrument_svc: InstrumentService,
        uow: UoW,
        subscription_repo: SubscriptionRepo,
    ) -> None:
        self._instrument_svc = instrument_svc
        self._subscription_repo = subscription_repo
        self._uow = uow

    def handle(self, user_id: int, data: CommandDeleteData) -> DeleteCommandResult:
        instrument = self._instrument_svc.get_or_create_by_ticker(data.ticker)
        kwargs = dict(user_id=user_id, instrument_id=instrument.identity)
        if not data.is_all:
            kwargs["price_in"] = data.prices
        deleted_rows = self._subscription_repo.delete_by(**kwargs)
        self._uow.commit()
        return DeleteCommandResult(deleted_count=deleted_rows)
