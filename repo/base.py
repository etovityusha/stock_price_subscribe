from abc import ABC, abstractmethod
from typing import Generic

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from models.orm.base import BaseORM
from models.types import DomainModel


class GenericRepository(Generic[DomainModel], ABC):
    @abstractmethod
    def get_by_id(self, id_: int) -> DomainModel | None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[DomainModel]:
        pass


class AlchemyGenericRepository(GenericRepository[DomainModel]):
    def __init__(
        self,
        session: Session,
        domain_model: type[DomainModel],
        orm_model: type[BaseORM],
    ) -> None:
        self._session = session
        self._domain_model = domain_model
        self._orm_model = orm_model

    def _construct_get_stmt(self, id_: int) -> Select:
        return select(self._orm_model).where(self._orm_model.id == id_)

    def get_by_id(self, id_: int) -> DomainModel | None:
        stmt = self._construct_get_stmt(id_)
        result = self._session.execute(stmt).first()
        if not result:
            return None
        return self._domain_model.model_validate(result[0])

    def _construct_find_all_stmt(self) -> Select:
        return select(self._orm_model)

    def find_all(self) -> list[DomainModel]:
        stmt = self._construct_find_all_stmt()
        result = self._session.execute(stmt).scalars().all()
        return [self._domain_model.model_validate(r) for r in result]
