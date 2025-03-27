from pydantic import BaseModel, Field


class BookBase(BaseModel):
    title: str = Field(...)
    author: str = Field(...)
    year: int = Field(...)


class Book(BookBase):
    id: int = Field(...)


class BookCreate(BookBase):
    pass
