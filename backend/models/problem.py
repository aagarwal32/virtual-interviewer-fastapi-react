import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.user import user_favorites

if TYPE_CHECKING:
    from models.user import User


class Difficulty(enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


problem_tags = Table(
    "problem_tags",
    Base.metadata,
    Column("problem_id", ForeignKey("problems.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # relationship
    problems: Mapped[list["Problem"]] = relationship(
        secondary=problem_tags, back_populates="tags"
    )


class Problem(Base):
    __tablename__ = "problems"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)

    # LeetCode's own numeric id (e.g. 3243)
    question_id: Mapped[int] = mapped_column(unique=True, index=True)

    # slug (e.g. "two-sum")
    task_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[Difficulty] = mapped_column(SqlEnum(Difficulty))

    # Pre-populates the Monaco editor
    starter_code: Mapped[str] = mapped_column(Text)

    # Imports + shared helper classes/functions (ListNode, TreeNode, etc.)
    execution_scaffold: Mapped[str] = mapped_column(Text)

    # invokes candidate solution
    entry_point: Mapped[str] = mapped_column(String(255))

    # optional
    reference_solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    solution_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # relationship
    tags: Mapped[list["Tag"]] = relationship(
        secondary=problem_tags, back_populates="problems"
    )
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="problem")
    favorited_by: Mapped[list["User"]] = relationship(
        secondary=user_favorites, back_populates="favorite_problems"
    )


class TestCase(Base):
    __tablename__ = "test_cases"

    # required
    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)

    input: Mapped[str] = mapped_column(Text)
    expected_output: Mapped[str] = mapped_column(Text)

    # ready-to-run assert statement for this case
    assertion_code: Mapped[str] = mapped_column(Text)

    # true for the first 3 sample cases shown to the user. False for hidden cases
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # relationship
    problem: Mapped["Problem"] = relationship(back_populates="test_cases")
