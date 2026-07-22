import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base

if TYPE_CHECKING:
    from models.interview import InterviewProblem


class SenderType(enum.Enum):
    USER = "user"
    LLM = "llm"


class Message(Base):
    """One turn of the chat transcript between the user and the interviewer LLM."""

    __tablename__ = "messages"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)
    interview_problem_id: Mapped[int] = mapped_column(
        ForeignKey("interview_problems.id"), index=True
    )

    # sender = user or llm
    sender: Mapped[SenderType] = mapped_column(SqlEnum(SenderType))

    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # relationship
    interview_problem: Mapped["InterviewProblem"] = relationship(
        back_populates="messages"
    )
