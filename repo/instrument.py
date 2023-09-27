import abc

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from enums import InstrumentTypeEnum
from models.domain.instument import Instrument
from models.orm.instrument import InstrumentORM
from repo.base import AlchemyGenericRepository


class InstrumentRepo(abc.ABC):
    @abc.abstractmethod
    def get_by_ticker(self, ticker: str) -> Instrument | None:
        pass

    @abc.abstractmethod
    def create(
        self,
        ticker: str,
        figi: str,
        isin: str,
        type_: InstrumentTypeEnum,
        precision: int,
    ) -> None:
        pass

    @abc.abstractmethod
    def find_by(self) -> list[Instrument]:
        pass


class InstrumentAlchemyRepo(InstrumentRepo, AlchemyGenericRepository[Instrument]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Instrument, InstrumentORM)

    def get_by_ticker(self, ticker: str) -> Instrument | None:
        stmt = select(InstrumentORM).where(InstrumentORM.ticker == ticker)
        orm_obj = self._session.execute(stmt).scalar_one_or_none()
        return self._domain_model.model_validate(orm_obj) if orm_obj else None

    def create(
        self,
        ticker: str,
        figi: str,
        isin: str,
        type_: InstrumentTypeEnum,
        precision: int,
    ) -> None:
        stmt = insert(self._orm_model).values(
            {
                "ticker": ticker,
                "figi": figi,
                "isin": isin,
                "type": type_,
                "precision": precision,
            }
        )
        self._session.execute(stmt)

    def find_by(self) -> list[Instrument]:
        return [Instrument.model_validate(x) for x in self._session.query(InstrumentORM).all()]
