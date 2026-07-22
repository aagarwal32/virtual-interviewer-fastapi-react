from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.problem import Problem
    from models.message import Message


class Interview(Base):
    __tablename__ = "interviews"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # seconds, whole interview
    time_allowed: Mapped[int] = mapped_column(Integer)

    time_remaining: Mapped[int] = mapped_column(Integer)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False)

    # optional
    # Aggregate results across all problems in the set. Completes, which 
    # lets an in-progress interview be distinguished from a failed one
    is_pass: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    superscore: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationship
    user: Mapped["User"] = relationship(back_populates="interviews")
    problem_attempts: Mapped[list["InterviewProblem"]] = relationship(
        back_populates="interview", order_by="InterviewProblem.order_index"
    )


class InterviewProblem(Base):
    """
    Association object between Interview and Problem - each row needs
    to carry its own progress state (is_solved, hints_used, etc), 
    not just the two foreign keys.

    One row per problem within a single interview.
    """

    __tablename__ = "interview_problems"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)

    # position within the set (0, 1, 2)
    order_index: Mapped[int] = mapped_column(Integer)

    is_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0)
    time_spent: Mapped[int] = mapped_column(Integer, default=0)  # seconds

    # optional
    # attempted -> code written, but not yet submitted
    # submitted -> latest submitted code for this interview-problem
    attempted_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # started/completed specific to this interview-problem
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationship
    interview: Mapped["Interview"] = relationship(back_populates="problem_attempts")
    problem: Mapped["Problem"] = relationship()
    messages: Mapped[list["Message"]] = relationship(
        back_populates="interview_problem", order_by="Message.created_at"
    )
