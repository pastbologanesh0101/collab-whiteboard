"""Flask-SocketIO glue for the Collaborative Whiteboard.

All of the actual room-state bookkeeping lives in board.py (a plain
Python module with no websocket dependency) so it can be unit tested in
isolation. This file just wires that logic up to Socket.IO events and
serves the single-page frontend.
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

from board import BoardManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "collab-whiteboard-dev-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

board = BoardManager()


@app.route("/")
def index():
    """Default landing page: sends the user into a fresh room."""
    return render_template("index.html", room_id="default")


@app.route("/room/<room_id>")
def room(room_id):
    """A specific whiteboard room, addressable by URL."""
    return render_template("index.html", room_id=room_id)


@socketio.on("join")
def on_join(data):
    """A client joined a room: subscribe them and send the current board."""
    room_id = data.get("room_id", "default")
    join_room(room_id)
    emit("board_state", {"strokes": board.get_state(room_id)})


@socketio.on("get_state")
def on_get_state(data):
    """Explicit request for the current state of a room (e.g. on demand)."""
    room_id = data.get("room_id", "default")
    emit("board_state", {"strokes": board.get_state(room_id)})


@socketio.on("draw_event")
def on_draw_event(data):
    """A client drew a stroke: store it and broadcast to the rest of the room."""
    room_id = data.get("room_id", "default")
    stroke = data.get("stroke")
    if stroke is None:
        return
    board.add_stroke(room_id, stroke)
    emit("draw_event", {"stroke": stroke}, to=room_id, include_self=False)


@socketio.on("clear_board")
def on_clear_board(data):
    """A client cleared the board: wipe stored state and tell everyone."""
    room_id = data.get("room_id", "default")
    board.clear_board(room_id)
    emit("board_cleared", {}, to=room_id)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
