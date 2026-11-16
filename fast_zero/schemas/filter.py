from pydantic import BaseModel, Field


class FilterPage(BaseModel):
    """Paginação: pula `offset` registros e retorna até `limit`."""

    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=100)
