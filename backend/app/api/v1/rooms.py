from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
import qrcode
import io
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.schemas.room import (
    RoomCreate,
    JoinRoom,
    RoomResponse,
    JoinRoomResponse,
    LeaderboardResponse
)
from app.services.room_service import (
    create_room,
    get_room_by_code,
    join_room,
    start_room,
    advance_question,
    end_room,
    get_leaderboard
)
from uuid import UUID

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_quiz_room(
    room_data: RoomCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Create a new quiz room. Only quiz owners can create rooms."""
    return create_room(db, room_data, current_user.id)


@router.get(
    "/{room_code}",
    response_model=RoomResponse
)
async def get_room(
    room_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get room details by room code."""
    return get_room_by_code(db, room_code)


@router.post(
    "/{room_code}/join",
    response_model=JoinRoomResponse
)
async def join_quiz_room(
    room_code: str,
    join_data: JoinRoom,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Join a quiz room as a registered user."""
    participant = join_room(
        db,
        room_code,
        join_data,
        user_id=current_user.id
    )
    room = get_room_by_code(db, room_code)
    return {
        "participant_id": participant.id,
        "nickname": participant.nickname,
        "room_code": room_code,
        "room_status": room.status,
        "message": f"Successfully joined room {room_code}"
    }


@router.post(
    "/{room_code}/start",
    response_model=RoomResponse
)
async def start_quiz_room(
    room_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Start the quiz. Only the host can do this."""
    return start_room(db, room_code, current_user.id)


@router.post(
    "/{room_code}/next",
    response_model=RoomResponse
)
async def next_question(
    room_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Advance to the next question."""
    return advance_question(db, room_code, current_user.id)


@router.post(
    "/{room_code}/end",
    response_model=RoomResponse
)
async def end_quiz_room(
    room_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """End the quiz session."""
    return end_room(db, room_code, current_user.id)


@router.get(
    "/{room_code}/leaderboard",
    response_model=LeaderboardResponse
)
async def get_room_leaderboard(
    room_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get current leaderboard for a room."""
    return get_leaderboard(db, room_code)

@router.get(
    "/{room_code}/qr",
    response_class=StreamingResponse
)
async def get_room_qr_code(
    room_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Generate a QR code for joining a quiz room.
    Students scan this to join instantly.
    """
    # Verify room exists
    room = get_room_by_code(db, room_code)

    # The URL students will land on when they scan
    join_url = f"http://localhost:5173/join/{room_code}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(join_url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes for streaming
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(
        img_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=room_{room_code}_qr.png"
        }
    )