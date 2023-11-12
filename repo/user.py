import abc
from typing import Sequence

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from models.domain.user import User
from models.orm.user import UserORM
from repo.base import AlchemyGenericRepository, GenericRepository


class UserRepo(GenericRepository[User], abc.ABC):
    @abc.abstractmethod
    def create(self, chat_id: int, username: str | None, phone: str | None) -> None:
        pass

    @abc.abstractmethod
    def find_by_chat_id(self, chat_id: int) -> Sequence[User]:
        pass


class UserAlchemyRepo(UserRepo, AlchemyGenericRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, User, UserORM)

    def create(self, chat_id: int, username: str | None, phone: str | None) -> None:
        stmt = insert(self._orm_model).values({"chat_id": chat_id, "username": username, "phone": phone})
        self._session.execute(stmt)

    def find_by_chat_id(self, chat_id: int) -> Sequence[User]:
        stmt = select(UserORM).where(UserORM.chat_id == chat_id)
        return [User.model_validate(x) for x in self._session.execute(stmt).scalars().all()]
