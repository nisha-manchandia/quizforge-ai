import uuid
from sqlalchemy import Column, String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models import Base

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Who created it
    creator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Quiz settings
    difficulty = Column(String(50), default="medium")
    is_public = Column(Boolean, default=False)
    time_limit = Column(Integer, default=30)

    # How was it created?
    generation_source = Column(String(50), default="manual")

    # draft → published
    status = Column(String(50), default="draft")

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    creator = relationship("User", back_populates="quizzes")
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )
    sessions = relationship("QuizSession", back_populates="quiz")

    def __repr__(self):
        return f"<Quiz {self.title} by {self.creator_id}>"


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Which quiz does this belong to?
    quiz_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False
    )

    # Question content
    question_text = Column(Text, nullable=False)

    # Stores {"A": "option1", "B": "option2", "C": "option3", "D": "option4"}
    options = Column(JSONB, nullable=False)

    # "A", "B", "C", or "D"
    correct_answer = Column(String(10), nullable=False)

    # AI generated explanation
    explanation = Column(Text, nullable=True)

    # Difficulty and ordering
    difficulty = Column(String(50), default="medium")
    order_index = Column(Integer, nullable=False)
    points = Column(Integer, default=100)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")

    def __repr__(self):
        return f"<Question {self.order_index} in quiz {self.quiz_id}>"