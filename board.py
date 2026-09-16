"""Pure room-state logic for the Collaborative Whiteboard.

This module has no knowledge of Flask, Flask-SocketIO, or websockets at
all. It just tracks, per room, the ordered list of strokes that have been
drawn so far. This separation lets us unit test the "what happens when a
stroke is added / a room is cleared / a new client asks for state" logic
without spinning up a real server or socket connection.

A "stroke" is any JSON-serializable object; in practice it's a dict like:

    {
        "points": [[x1, y1], [x2, y2], ...],
        "color": "#ff0000",
        "width": 3,
    }

but this module treats it as an opaque value and only cares about order.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List


class BoardManager:
    """Tracks strokes for any number of independent whiteboard rooms."""

    def __init__(self) -> None:
        self._rooms: Dict[str, List[Any]] = {}
        self._lock = threading.Lock()

    def add_stroke(self, room_id: str, stroke: Any) -> None:
        """Append a stroke to the given room's history.

        Creates the room if it doesn't exist yet.
        """
        with self._lock:
            self._rooms.setdefault(room_id, []).append(stroke)

    def get_state(self, room_id: str) -> List[Any]:
        """Return the ordered list of strokes for a room.

        Returns an empty list (not an error) for a room that has never
        had any strokes. The returned list is a copy, so callers can't
        mutate internal state by accident.
        """
        with self._lock:
            return list(self._rooms.get(room_id, []))

    def clear_board(self, room_id: str) -> None:
        """Remove all strokes for a room, leaving it empty (but present)."""
        with self._lock:
            self._rooms[room_id] = []

    def room_exists(self, room_id: str) -> bool:
        with self._lock:
            return room_id in self._rooms

    def stroke_count(self, room_id: str) -> int:
        with self._lock:
            return len(self._rooms.get(room_id, []))
