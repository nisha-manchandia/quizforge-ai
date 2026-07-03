from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class RoomCreate(BaseModel):
    """Schema for creating a quiz room."""
    quiz_id: UUID
    max_participants: int = 100
    is_team_mode: bool = False


class JoinRoom(BaseModel):
    """Schema for joining a room."""
    nickname: str


class RoomResponse(BaseModel):
    """Schema for room details."""
    id: UUID
    quiz_id: UUID
    host_id: UUID
    room_code: str
    status: str
    current_question: int
    max_participants: int
    is_team_mode: bool
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    """Schema for a participant in a room."""
    id: UUID
    session_id: UUID
    user_id: Optional[UUID]
    nickname: str
    is_guest: bool
    joined_at: datetime

    class Config:
        from_attributes = True


class JoinRoomResponse(BaseModel):
    """Schema returned when successfully joining a room."""
    participant_id: UUID
    nickname: str
    room_code: str
    room_status: str
    message: str


class LeaderboardEntry(BaseModel):
    """Single entry in the leaderboard."""
    rank: int
    nickname: str
    score: int
    correct_answers: int


class LeaderboardResponse(BaseModel):
    """Full leaderboard for a room."""
    room_code: str
    entries: List[LeaderboardEntry]