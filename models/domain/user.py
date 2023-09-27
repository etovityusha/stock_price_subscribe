from models.domain.base import BaseDomain


class User(BaseDomain):
    chat_id: int
    username: str | None
    phone: str | None
