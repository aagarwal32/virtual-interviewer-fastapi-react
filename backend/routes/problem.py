from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.security import authenticate_user
from db.database import get_db
from models import User, Problem
from schemas.problem import (
    ProblemBasicResponse, ProblemDetailResponse, ProblemListResponse
    )

router = APIRouter(prefix="/problem", tags=["problem"])


@router.get("/list", response_model=ProblemListResponse)
async def problem_list(db: Session = Depends(get_db)) -> ProblemListResponse:
    problems = (db.query(Problem)
                .order_by(Problem.question_id)
                .limit(100)
                .all()
                )

    return ProblemListResponse(
        problem_list=[ProblemBasicResponse.model_validate(p) for p in problems])