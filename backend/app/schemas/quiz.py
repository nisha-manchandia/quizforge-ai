from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ─── Question Schemas ──────────────────────────────────────────

class QuestionCreate(BaseModel):
    """Schema for creating a question."""
    question_text: str
    options: dict          # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer: str    # "A", "B", "C", or "D"
    explanation: Optional[str] = None
    difficulty: str = "medium"
    order_index: int
    points: int = 100

class QuestionResponse(BaseModel):
    """Schema for returning a question."""
    id: UUID
    quiz_id: UUID
    question_text: str
    options: dict
    correct_answer: str
    explanation: Optional[str]
    difficulty: str
    order_index: int
    points: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Quiz Schemas ──────────────────────────────────────────────

class QuizCreate(BaseModel):
    """Schema for creating a quiz."""
    title: str
    description: Optional[str] = None
    difficulty: str = "medium"
    is_public: bool = False
    time_limit: int = 30
    questions: Optional[List[QuestionCreate]] = []

class QuizUpdate(BaseModel):
    """Schema for updating a quiz — all fields optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    is_public: Optional[bool] = None
    time_limit: Optional[int] = None
    status: Optional[str] = None

class QuizResponse(BaseModel):
    """Schema for returning a quiz without questions."""
    id: UUID
    title: str
    description: Optional[str]
    creator_id: UUID
    difficulty: str
    is_public: bool
    time_limit: int
    generation_source: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuizDetailResponse(BaseModel):
    """Schema for returning a quiz WITH its questions."""
    id: UUID
    title: str
    description: Optional[str]
    creator_id: UUID
    difficulty: str
    is_public: bool
    time_limit: int
    generation_source: str
    status: str
    created_at: datetime
    updated_at: datetime
    questions: List[QuestionResponse] = []

    class Config:
        from_attributes = True