import abc

from models.domain.user import User
from repo.user import UserRepo


class UserServiceError(Exception):
    pass


class UserService(abc.ABC):
    @abc.abstractmethod
    def get_user_by_chat_id(self, chat_id) -> User:
        pass


class DefaultUserService(UserService):
    def __init__(self, user_repo: UserRepo) -> None:
        self._user_repo = user_repo

    def get_user_by_chat_id(self, chat_id) -> User:
        users = self._user_repo.find_by_chat_id(chat_id=chat_id)
        if len(users) != 1:
            raise UserServiceError
        return users[0]
