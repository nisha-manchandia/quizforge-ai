from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from datetime import datetime, timezone


class ConnectionManager:
    """
    Manages all active WebSocket connections across all quiz rooms.
    
    Structure:
    {
      "ABC123": {websocket1, websocket2, websocket3},
      "XYZ789": {websocket4, websocket5}
    }
    """

    def __init__(self):
        # room_code → set of active WebSocket connections
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        # websocket → player info
        self.player_info: Dict[WebSocket, dict] = {}

    async def connect(
        self,
        websocket: WebSocket,
        room_code: str,
        nickname: str
    ):
        """Accept a new WebSocket connection and add to room."""
        await websocket.accept()

        if room_code not in self.active_rooms:
            self.active_rooms[room_code] = set()

        self.active_rooms[room_code].add(websocket)
        self.player_info[websocket] = {
            "room_code": room_code,
            "nickname": nickname,
            "joined_at": datetime.now(timezone.utc).isoformat()
        }

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection when player leaves."""
        if websocket in self.player_info:
            room_code = self.player_info[websocket]["room_code"]

            if room_code in self.active_rooms:
                self.active_rooms[room_code].discard(websocket)

                # Clean up empty rooms
                if not self.active_rooms[room_code]:
                    del self.active_rooms[room_code]

            del self.player_info[websocket]

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to one specific player."""
        await websocket.send_text(json.dumps(message))

    async def broadcast_to_room(self, room_code: str, message: dict):
        """Send a message to ALL players in a room."""
        if room_code not in self.active_rooms:
            return

        disconnected = set()
        for websocket in self.active_rooms[room_code].copy():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.add(websocket)

        # Clean up any broken connections
        for websocket in disconnected:
            self.disconnect(websocket)

    def get_player_count(self, room_code: str) -> int:
        """Get number of connected players in a room."""
        return len(self.active_rooms.get(room_code, set()))

    def get_player_nickname(self, websocket: WebSocket) -> str:
        """Get nickname of a connected player."""
        return self.player_info.get(websocket, {}).get("nickname", "Unknown")


# Single global instance — shared across all WebSocket connections
manager = ConnectionManager()