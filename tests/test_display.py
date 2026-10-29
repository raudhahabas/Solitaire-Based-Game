import re
import unittest

from solitaire.display import render_board
from solitaire.game import COMPLETE_RUN, GameState

ANSI_CODE = re.compile(r"\033\[[0-9;]*m")


def plain(text):
    return ANSI_CODE.sub("", text)


class RenderBoardTest(unittest.TestCase):
    def test_columns_grow_upwards_from_labels(self):
        state = GameState([[9, 8], [3], [], [], [], []])
        lines = [line.rstrip() for line in plain(render_board(state)).splitlines()]
        self.assertEqual(lines, [" 8", " 9   3", " A   B   C   D   E   F"])

    def test_complete_stack_hides_numbers(self):
        state = GameState([list(COMPLETE_RUN), [], [], [], [], []])
        state.complete[0] = True
        rows = plain(render_board(state)).splitlines()[:-1]
        self.assertTrue(all(row.strip() == "" for row in rows))

    def test_blocked_top_card_uses_grey(self):
        state = GameState([[9, 2], [], [], [], [], []])
        state.blocked[0] = True
        top_row = render_board(state).splitlines()[0]
        self.assertIn("\033[48;2;204;204;204m 2 ", top_row)


if __name__ == "__main__":
    unittest.main()
