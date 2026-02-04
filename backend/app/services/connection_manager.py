from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """
    Manages WebSocket connections for game rooms.

    Each game has a room identified by its code.
    Players in the same room receive broadcasts of moves.
    """

    def __init__(self):
        # game_code -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> (game_code, user_id)
        self.connection_info: Dict[WebSocket, tuple[str, int]] = {}

    async def connect(self, websocket: WebSocket, game_code: str, user_id: int):
        """Accept a WebSocket connection and add it to a game room."""
        await websocket.accept()

        if game_code not in self.active_connections:
            self.active_connections[game_code] = set()

        self.active_connections[game_code].add(websocket)
        self.connection_info[websocket] = (game_code, user_id)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from its game room."""
        if websocket in self.connection_info:
            game_code, _ = self.connection_info[websocket]

            if game_code in self.active_connections:
                self.active_connections[game_code].discard(websocket)

                # Clean up empty rooms
                if not self.active_connections[game_code]:
                    del self.active_connections[game_code]

            del self.connection_info[websocket]

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific connection."""
        await websocket.send_json(message)

    async def broadcast_to_game(self, game_code: str, message: dict, exclude: WebSocket = None):
        """Broadcast a message to all connections in a game room."""
        if game_code not in self.active_connections:
            return

        for connection in self.active_connections[game_code]:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might be closed
                    pass

    async def broadcast_to_all(self, game_code: str, message: dict):
        """Broadcast a message to all connections in a game room including sender."""
        if game_code not in self.active_connections:
            return

        for connection in self.active_connections[game_code]:
            try:
                await connection.send_json(message)
            except Exception:
                pass

    def get_connection_count(self, game_code: str) -> int:
        """Get the number of connections in a game room."""
        return len(self.active_connections.get(game_code, set()))

    def get_user_id(self, websocket: WebSocket) -> int | None:
        """Get the user ID associated with a WebSocket connection."""
        if websocket in self.connection_info:
            return self.connection_info[websocket][1]
        return None


# Global connection manager instance
manager = ConnectionManager()
