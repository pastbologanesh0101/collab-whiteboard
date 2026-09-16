# Collaborative Whiteboard

A real-time, room-based collaborative whiteboard built with Flask and
Flask-SocketIO. Anyone who opens the same room URL sees the same board and
everyone's strokes appear live, for everyone else, as they're drawn.

## How it works

- **Backend (`app.py` + `board.py`)** - Clients join a "room" (identified by
  a room id in the URL, e.g. `/room/team-standup`). Each stroke a client
  draws (a sequence of `[x, y]` points plus a color and width) is sent to
  the server over a `draw_event` socket event, stored in memory for that
  room, and rebroadcast to everyone else currently in the room. When a new
  client joins, it asks for the current board via a `get_state`/`board_state`
  round trip and replays every stroke drawn so far, in order, so latecomers
  see the full picture instead of a blank canvas.

  All of that room bookkeeping - add a stroke, fetch a room's current
  strokes, clear a room, keep rooms isolated from each other - lives in
  `board.py`, a small dependency-free module with no Flask or websocket
  code in it at all. `app.py` is just the Socket.IO glue on top. This split
  is what makes the core logic unit-testable without a running server.

- **Frontend (`templates/index.html`)** - A single page with a `<canvas>`,
  a color picker, a stroke-width slider, and a "Clear board" button, all in
  vanilla JS. Mouse events capture points locally while you drag, emit the
  finished stroke over `socket.io-client` (loaded from a CDN `<script>`
  tag), and render every stroke - your own and everyone else's - as it
  arrives.

## Running it

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **two** browser tabs (or two different browsers) at:

```
http://localhost:5000/room/demo
```

Draw in one tab and watch the stroke appear in the other, live. Open a
third tab at `http://localhost:5000/room/demo` at any point and it will
replay the whole board's history instantly. A different room id (e.g.
`/room/another-room`) gets its own, completely independent board.

## Running the tests

The pure room-state logic in `board.py` has a full unit test suite that
doesn't require a running server:

```bash
python -m unittest discover -s tests -v
```

These are the same tests run automatically on every push/PR by the GitHub
Actions workflow in `.github/workflows/tests.yml` (Python 3.11 and 3.12).
Deliberately out of scope for CI: the live websocket server itself - that's
integration-level behavior best verified by actually opening two tabs, as
above.

## Project layout

```
app.py                  Flask + Flask-SocketIO app: routes and socket events
board.py                Pure, testable room/stroke state manager
templates/index.html    Single-page canvas frontend
tests/test_board.py     Unit tests for board.py
.github/workflows/      CI: runs the unit tests on push/PR
```

## License

MIT - see [LICENSE](LICENSE).
