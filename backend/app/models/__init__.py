from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models here so SQLAlchemy can resolve relationships
from app.models.user import User
from app.models.quiz import Quiz, Question
from app.models.room import QuizSession, SessionParticipant, ParticipantAnswer