import abc
import decimal

from sqlalchemy.orm import Session

from models.domain.instrument_price import InstrumentPrice
from models.orm.instrument_price import InstrumentPriceORM
from repo.base import AlchemyGenericRepository


class InstrumentPriceRepo(abc.ABC):
    @abc.abstractmethod
    def create_or_update(self, instrument_id: int, price: decimal.Decimal) -> decimal.Decimal | None:
        """Return old price"""
        pass

    @abc.abstractmethod
    def get_by_instrument_id(self, instrument_id: int) -> InstrumentPrice | None:
        pass


class InstrumentPriceAlchemyRepo(InstrumentPriceRepo, AlchemyGenericRepository[InstrumentPrice]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, InstrumentPrice, InstrumentPriceORM)

    def create_or_update(self, instrument_id: int, price: decimal.Decimal) -> decimal.Decimal | None:
        instrument_price = self.get_by_instrument_id(instrument_id=instrument_id)
        if instrument_price is None:
            new_instrument_price = InstrumentPriceORM(instrument_id=instrument_id, price=price)
            self._session.add(new_instrument_price)
            return None
        self._session.query(InstrumentPriceORM).filter(InstrumentPriceORM.instrument_id == instrument_id).update(
            {"price": price}
        )
        return instrument_price.price

    def get_by_instrument_id(self, instrument_id: int) -> InstrumentPrice | None:
        orm_obj = self._get_orm_obj_by_instrument_id(instrument_id=instrument_id)
        return InstrumentPrice.model_validate(orm_obj) if orm_obj else None

    def _get_orm_obj_by_instrument_id(self, instrument_id: int) -> InstrumentPriceORM | None:
        return (
            self._session.query(InstrumentPriceORM)
            .filter(InstrumentPriceORM.instrument_id == instrument_id)
            .one_or_none()
        )
