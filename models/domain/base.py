from pydantic import BaseModel, Field


class BaseDomain(BaseModel):
    identity: int | None = Field(alias="id", default=None)

    class Config:
        from_attributes = True
