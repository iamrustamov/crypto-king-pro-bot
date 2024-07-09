from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["UserModel"]

from db.base_model import AsyncBase


class UserModel(AsyncBase):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )

    username: Mapped[str | None] = mapped_column(String(32))
    create_datetime: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    __mapper_args__ = {"eager_defaults": True}

    def __str__(self) -> str:
        username = "empty"
        if self.username:
            username = f"@{self.username}"
        return (
            f"id: {self.user_id} | username: {username}"
        )
