from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
