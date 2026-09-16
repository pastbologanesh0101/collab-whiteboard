"""Unit tests for board.py -- the pure room-state logic.

These tests exercise BoardManager directly and never touch Flask,
Flask-SocketIO, or a real network connection, so they run fast and
don't need a live server (deliberately excluded from CI's websocket
surface, per the project's testing strategy).
"""

import unittest

from board import BoardManager


def make_stroke(*points, color="#000000", width=3):
    return {"points": list(points), "color": color, "width": width}


class TestBoardManager(unittest.TestCase):
    def setUp(self):
        self.board = BoardManager()

    def test_new_room_has_empty_state(self):
        self.assertEqual(self.board.get_state("room-1"), [])

    def test_add_stroke_appears_in_state(self):
        stroke = make_stroke([0, 0], [10, 10])
        self.board.add_stroke("room-1", stroke)
        self.assertEqual(self.board.get_state("room-1"), [stroke])

    def test_multiple_strokes_preserve_order(self):
        first = make_stroke([0, 0], [1, 1])
        second = make_stroke([5, 5], [6, 6])
        third = make_stroke([9, 9], [10, 10])
        self.board.add_stroke("room-1", first)
        self.board.add_stroke("room-1", second)
        self.board.add_stroke("room-1", third)
        self.assertEqual(
            self.board.get_state("room-1"), [first, second, third]
        )

    def test_clear_board_empties_state(self):
        self.board.add_stroke("room-1", make_stroke([0, 0], [1, 1]))
        self.board.clear_board("room-1")
        self.assertEqual(self.board.get_state("room-1"), [])

    def test_strokes_isolated_per_room(self):
        stroke_a = make_stroke([0, 0], [1, 1], color="#ff0000")
        stroke_b = make_stroke([2, 2], [3, 3], color="#00ff00")
        self.board.add_stroke("room-a", stroke_a)
        self.board.add_stroke("room-b", stroke_b)
        self.assertEqual(self.board.get_state("room-a"), [stroke_a])
        self.assertEqual(self.board.get_state("room-b"), [stroke_b])

    def test_clearing_one_room_does_not_affect_another(self):
        stroke_a = make_stroke([0, 0], [1, 1])
        stroke_b = make_stroke([2, 2], [3, 3])
        self.board.add_stroke("room-a", stroke_a)
        self.board.add_stroke("room-b", stroke_b)
        self.board.clear_board("room-a")
        self.assertEqual(self.board.get_state("room-a"), [])
        self.assertEqual(self.board.get_state("room-b"), [stroke_b])

    def test_room_exists_reflects_activity(self):
        self.assertFalse(self.board.room_exists("room-1"))
        self.board.add_stroke("room-1", make_stroke([0, 0], [1, 1]))
        self.assertTrue(self.board.room_exists("room-1"))

    def test_stroke_count(self):
        self.assertEqual(self.board.stroke_count("room-1"), 0)
        self.board.add_stroke("room-1", make_stroke([0, 0], [1, 1]))
        self.board.add_stroke("room-1", make_stroke([2, 2], [3, 3]))
        self.assertEqual(self.board.stroke_count("room-1"), 2)

    def test_get_state_returns_copy_not_reference(self):
        self.board.add_stroke("room-1", make_stroke([0, 0], [1, 1]))
        state = self.board.get_state("room-1")
        state.append(make_stroke([9, 9], [8, 8]))
        # Mutating the returned list must not affect internal state.
        self.assertEqual(self.board.stroke_count("room-1"), 1)


if __name__ == "__main__":
    unittest.main()
