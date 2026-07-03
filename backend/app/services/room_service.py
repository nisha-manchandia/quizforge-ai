from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.room import QuizSession, SessionParticipant, ParticipantAnswer
from app.models.quiz import Quiz
from app.schemas.room import RoomCreate, JoinRoom
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
import random
import string


def generate_room_code(length: int = 6) -> str:
    """Generate a random uppercase room code like ABC123."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))


def create_room(
    db: Session,
    room_data: RoomCreate,
    host_id: UUID
) -> QuizSession:
    """
    Create a new quiz room.
    Only the quiz owner can create a room for their quiz.
    """
    # Verify quiz exists and host owns it
    quiz = db.query(Quiz).filter(Quiz.id == room_data.quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if quiz.creator_id != host_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this quiz"
        )

    # Generate unique room code
    while True:
        room_code = generate_room_code()
        existing = db.query(QuizSession).filter(
            QuizSession.room_code == room_code,
            QuizSession.status != "finished"
        ).first()
        if not existing:
            break

    # Create the session
    session = QuizSession(
        quiz_id=room_data.quiz_id,
        host_id=host_id,
        room_code=room_code,
        status="waiting",
        current_question=0,
        max_participants=room_data.max_participants,
        is_team_mode=room_data.is_team_mode
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_room_by_code(db: Session, room_code: str) -> QuizSession:
    """Get a room by its room code."""
    room = db.query(QuizSession).filter(
        QuizSession.room_code == room_code.upper()
    ).first()

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    return room


def join_room(
    db: Session,
    room_code: str,
    join_data: JoinRoom,
    user_id: Optional[UUID] = None
) -> SessionParticipant:
    """
    Join a quiz room.
    Works for both registered users and guests.
    """
    from typing import Optional

    room = get_room_by_code(db, room_code)

    # Room must be in waiting state
    if room.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This quiz has already ended"
        )

    if room.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz is already in progress"
        )

    # Check participant limit
    current_count = db.query(SessionParticipant).filter(
        SessionParticipant.session_id == room.id
    ).count()

    if current_count >= room.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is full"
        )

    # Prevent duplicate join for registered users
    if user_id:
        existing = db.query(SessionParticipant).filter(
            SessionParticipant.session_id == room.id,
            SessionParticipant.user_id == user_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already joined this room"
            )

    # Create participant record
    participant = SessionParticipant(
        session_id=room.id,
        user_id=user_id,
        nickname=join_data.nickname,
        is_guest=user_id is None
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def start_room(
    db: Session,
    room_code: str,
    host_id: UUID
) -> QuizSession:
    """Start a quiz session. Only the host can start."""
    from datetime import datetime, timezone

    room = get_room_by_code(db, room_code)

    if room.host_id != host_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can start the quiz"
        )

    if room.status != "waiting":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start a room with status: {room.status}"
        )

    room.status = "active"
    room.current_question = 0
    room.started_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(room)
    return room


def advance_question(
    db: Session,
    room_code: str,
    host_id: UUID
) -> QuizSession:
    """Move to the next question."""
    room = get_room_by_code(db, room_code)

    if room.host_id != host_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can advance questions"
        )

    if room.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz is not active"
        )

    room.current_question += 1
    db.commit()
    db.refresh(room)
    return room


def end_room(
    db: Session,
    room_code: str,
    host_id: UUID
) -> QuizSession:
    """End a quiz session."""
    from datetime import datetime, timezone

    room = get_room_by_code(db, room_code)

    if room.host_id != host_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can end the quiz"
        )

    room.status = "finished"
    room.ended_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(room)
    return room


def get_leaderboard(
    db: Session,
    room_code: str
) -> dict:
    """
    Get current leaderboard for a room.
    Calculates scores from participant_answers table.
    """
    from app.models.room import ParticipantAnswer

    room = get_room_by_code(db, room_code)

    participants = db.query(SessionParticipant).filter(
        SessionParticipant.session_id == room.id
    ).all()

    leaderboard = []

    for participant in participants:
        answers = db.query(ParticipantAnswer).filter(
            ParticipantAnswer.participant_id == participant.id
        ).all()

        total_score = sum(a.points_earned for a in answers)
        correct = sum(1 for a in answers if a.is_correct)

        leaderboard.append({
            "nickname": participant.nickname,
            "score": total_score,
            "correct_answers": correct
        })

    # Sort by score descending
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    # Add rank
    ranked = [
        {
            "rank": i + 1,
            "nickname": entry["nickname"],
            "score": entry["score"],
            "correct_answers": entry["correct_answers"]
        }
        for i, entry in enumerate(leaderboard)
    ]

    return {
        "room_code": room_code,
        "entries": ranked
    }