import enum


class SubscriptionTypeEnum(str, enum.Enum):
    ALWAYS = "ALWAYS"
    ONETIME = "ONETIME"
    CROSSING = "CROSSING"

    @staticmethod
    def get_default() -> "SubscriptionTypeEnum":
        return SubscriptionTypeEnum.ALWAYS


class InstrumentTypeEnum(str, enum.Enum):
    SHARE = "SHARE"
    BOND = "BOND"
    FUTURES = "FUTURES"
    CURRENCY = "CURRENCY"
    ETF = "ETF"


class CommandTypeEnum(str, enum.Enum):
    ADD = "ADD"
    STEP = "STEP"
    PRICE = "PRICE"
    DELETE = "DELETE"
    DELETE_ALL = "DELETE_ALL"
    MY = "MY"


class LocaleEnum(str, enum.Enum):
    RU = "RU"
    EN = "EN"
