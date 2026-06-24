import uuid
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What quiz is being played
    quiz_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id"),
        nullable=False
    )

    # Who is hosting
    host_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    # Join code for participants
    room_code = Column(String(10), unique=True, nullable=False)

    # State machine
    status = Column(String(50), default="waiting")
    current_question = Column(Integer, default=0)

    # Settings
    max_participants = Column(Integer, default=100)
    is_team_mode = Column(Boolean, default=False)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    quiz = relationship("Quiz", back_populates="sessions")
    host = relationship("User", back_populates="hosted_sessions")
    participants = relationship(
        "SessionParticipant",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<QuizSession {self.room_code} status={self.status}>"


class SessionParticipant(Base):
    __tablename__ = "session_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True  # guests have no user account
    )

    nickname = Column(String(100), nullable=False)
    is_guest = Column(Boolean, default=False)
    team_id = Column(UUID(as_uuid=True), nullable=True)
    joined_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Prevents same user joining twice
    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="uq_session_user"),
    )

    # Relationships
    session = relationship("QuizSession", back_populates="participants")
    answers = relationship("ParticipantAnswer", back_populates="participant")

    def __repr__(self):
        return f"<Participant {self.nickname} in {self.session_id}>"


class ParticipantAnswer(Base):
    __tablename__ = "participant_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    participant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("session_participants.id"),
        nullable=False
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id"),
        nullable=False
    )

    selected_answer = Column(String(10), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, nullable=False)
    points_earned = Column(Integer, default=0)
    answered_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # Prevents double submission
    __table_args__ = (
        UniqueConstraint(
            "participant_id",
            "question_id",
            name="uq_participant_question"
        ),
    )

    # Relationships
    participant = relationship("SessionParticipant", back_populates="answers")

    def __repr__(self):
        return f"<Answer by {self.participant_id} for {self.question_id}>"