import abc

from pydantic import BaseModel

from repo.subscription import SubscriptionRepo
from services.commands.dto import CommandDeleteAllData
from services.uow import UoW


class DeleteCommandResult(BaseModel):
    deleted_count: int | None


class DeleteAllCommandHandler(abc.ABC):
    @abc.abstractmethod
    def handle(self, user_id: int, data: CommandDeleteAllData) -> DeleteCommandResult:
        pass


class DefaultDeleteAllCommandHandler(DeleteAllCommandHandler):
    def __init__(
        self,
        uow: UoW,
        subscription_repo: SubscriptionRepo,
    ) -> None:
        self._subscription_repo = subscription_repo
        self._uow = uow

    def handle(self, user_id: int, data: CommandDeleteAllData) -> DeleteCommandResult:
        deleted_rows = self._subscription_repo.delete_by(user_id=user_id)
        self._uow.commit()
        return DeleteCommandResult(deleted_count=deleted_rows)
