from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class AsyncBase(AsyncAttrs, DeclarativeBase):
    pass
