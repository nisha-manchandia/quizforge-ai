from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.websockets.room_socket import manager
from app.services.redis_service import (
    update_leaderboard,
    increment_score,
    get_leaderboard,
    record_answer,
    add_active_player,
    remove_active_player,
    set_player_state,
    get_player_state
)
from app.models.room import QuizSession, SessionParticipant
from app.models.quiz import Question
from app.core.security import decode_access_token
import json
from datetime import datetime, timezone

router = APIRouter(tags=["WebSocket"])


def calculate_points(
    is_correct: bool,
    time_taken: float,
    time_limit: int,
    base_points: int = 1000
) -> int:
    """
    Calculate points based on correctness and speed.
    Faster correct answers earn more points — like Kahoot.
    """
    if not is_correct:
        return 0

    # Speed bonus: up to 50% extra for answering instantly
    time_ratio = max(0, (time_limit - time_taken) / time_limit)
    speed_bonus = int(base_points * 0.5 * time_ratio)

    return base_points + speed_bonus


@router.websocket("/ws/room/{room_code}")
async def websocket_room(
    websocket: WebSocket,
    room_code: str,
    token: str = None,
    nickname: str = "Guest",
    db: Session = Depends(get_db)
):
    """
    Main WebSocket endpoint for quiz rooms.
    
    Connect: ws://localhost:8000/ws/room/ABC123?token=eyJ...&nickname=Nisha
    """

    # ── Authenticate user if token provided ──
    user_id = None
    if token:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("sub")
            nickname = payload.get("email", nickname).split("@")[0]

    # ── Validate room exists ──
    room = db.query(QuizSession).filter(
        QuizSession.room_code == room_code.upper()
    ).first()

    if not room:
        await websocket.accept()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Room not found"
        }))
        await websocket.close()
        return

    # ── Connect player ──
    await manager.connect(websocket, room_code, nickname)
    add_active_player(room_code, nickname)
    update_leaderboard(room_code, nickname, 0)

    player_count = manager.get_player_count(room_code)

    # ── Notify everyone someone joined ──
    await manager.broadcast_to_room(room_code, {
        "type": "player_joined",
        "nickname": nickname,
        "player_count": player_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # ── Send welcome message to this player ──
    await manager.send_personal(websocket, {
        "type": "connected",
        "room_code": room_code,
        "nickname": nickname,
        "room_status": room.status,
        "message": f"Welcome to room {room_code}!"
    })

    try:
        while True:
            # Wait for messages from this player
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                continue

            message_type = message.get("type")

            # ── Handle: submit_answer ──
            if message_type == "submit_answer":
                question_index = message.get("question_index", 0)
                selected_answer = message.get("answer")
                time_taken = float(message.get("time_taken", 30))

                # Prevent duplicate submissions
                is_first = record_answer(room_code, question_index, nickname)
                if not is_first:
                    await manager.send_personal(websocket, {
                        "type": "answer_rejected",
                        "message": "Answer already submitted"
                    })
                    continue

                # Get the question from database
                questions = db.query(Question).filter(
                    Question.quiz_id == room.quiz_id
                ).order_by(Question.order_index).all()

                if question_index >= len(questions):
                    await manager.send_personal(websocket, {
                        "type": "error",
                        "message": "Invalid question index"
                    })
                    continue

                question = questions[question_index]
                is_correct = selected_answer == question.correct_answer

                # Calculate and award points
                points = calculate_points(
                    is_correct=is_correct,
                    time_taken=time_taken,
                    time_limit=room.quiz.time_limit if hasattr(room, 'quiz') else 30
                )

                # Update Redis leaderboard atomically
                new_score = increment_score(room_code, nickname, points)

                # Send result to this player
                await manager.send_personal(websocket, {
                    "type": "answer_result",
                    "correct": is_correct,
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation,
                    "points_earned": points,
                    "total_score": int(new_score)
                })

                # Broadcast updated leaderboard to ALL players
                leaderboard = get_leaderboard(room_code)
                await manager.broadcast_to_room(room_code, {
                    "type": "leaderboard_update",
                    "entries": leaderboard
                })

            # ── Handle: ping ──
            elif message_type == "ping":
                await manager.send_personal(websocket, {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

            # ── Handle: get_leaderboard ──
            elif message_type == "get_leaderboard":
                leaderboard = get_leaderboard(room_code)
                await manager.send_personal(websocket, {
                    "type": "leaderboard_update",
                    "entries": leaderboard
                })

            # ── Handle: unknown message type ──
            else:
                await manager.send_personal(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        remove_active_player(room_code, nickname)

        # Notify room that player left
        await manager.broadcast_to_room(room_code, {
            "type": "player_left",
            "nickname": nickname,
            "player_count": manager.get_player_count(room_code)
        })