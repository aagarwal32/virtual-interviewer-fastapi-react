from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from models.problem import Difficulty
from schemas.user import UserResponse


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class TestCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    assertion_code: str
    is_sample: bool
    order_index: int


class ProblemBasicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    question_id: int
    task_id: str
    title: str
    difficulty: Difficulty

    tags: List[TagResponse]


class ProblemDetailResponse(ProblemBasicResponse):
    description: str
    starter_code: str
    execution_scaffold: str
    entry_point: str

    reference_solution: Optional[str] = None
    solution_explanation: Optional[str] = None

    test_cases: List[TestCaseResponse]


class ProblemListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    problem_list: List[ProblemBasicResponse]
