import decimal
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from enums import SubscriptionTypeEnum


class CommandData(BaseModel):
    pass


class TickerCommandData(CommandData):
    ticker: str

    @field_validator("ticker", mode="before")
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper() if isinstance(v, str) else v


class CommandAddData(TickerCommandData):
    prices: list[decimal.Decimal]
    type: SubscriptionTypeEnum = Field(default=SubscriptionTypeEnum.ALWAYS)

    @field_validator("ticker", mode="before")
    def uppercase_ticker(cls, v: str) -> str:
        return v.upper() if isinstance(v, str) else v


class CommandStepData(TickerCommandData):
    price_from: decimal.Decimal
    price_to: decimal.Decimal
    step: decimal.Decimal
    type: SubscriptionTypeEnum = Field(default=SubscriptionTypeEnum.ALWAYS)


class CommandDeleteData(TickerCommandData):
    prices: list[decimal.Decimal] | None
    is_all: bool = False

    @model_validator(mode="before")
    def set_prices_to_null_if_is_all(cls, data: dict[str, Any]) -> dict[str, Any]:
        if "is_all" in data and data["is_all"]:
            data["prices"] = None
        return data


class CommandPriceData(TickerCommandData):
    pass


class CommandDeleteAllData(CommandData):
    pass


class CommandMyData(CommandData):
    pass
