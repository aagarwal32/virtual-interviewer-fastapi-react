from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base

if TYPE_CHECKING:
    from models.interview import Interview
    from models.problem import Problem

user_favorites = Table(
    "user_favorites",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("problem_id", ForeignKey("problems.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # optional
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # relationship
    interviews: Mapped[list["Interview"]] = relationship(back_populates="user")
    favorite_problems: Mapped[list["Problem"]] = relationship(
        secondary=user_favorites, back_populates="favorited_by"
    )
