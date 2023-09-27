import abc

from repo.user import UserRepo
from services.uow import UoW


class AlreadyRegisteredError(Exception):
    pass


class RegistrationService(abc.ABC):
    def register_user(self, **kwargs) -> None:
        pass


class TelegramBotRegistrationService(RegistrationService):
    def __init__(self, uow: UoW, user_repo: UserRepo) -> None:
        self._user_repo = user_repo
        self._uow = uow

    def register_user(self, chat_id: int, username: str | None, phone: str | None) -> None:
        if self._user_repo.find_by_chat_id(chat_id=chat_id):
            raise AlreadyRegisteredError
        self._user_repo.create(chat_id=chat_id, username=username, phone=phone)
        self._uow.commit()
