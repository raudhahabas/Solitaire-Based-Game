import random
import unittest
from collections import Counter

from solitaire.game import (
    COMPLETE_RUN,
    Command,
    GameState,
    Move,
    apply_move,
    is_valid_move,
    is_won,
    new_game,
    parse_command,
)


def board(*stacks, blocked=(), complete=()):
    """Build a 6-stack board; unspecified stacks are empty."""
    stacks = [list(s) for s in stacks] + [[] for _ in range(6 - len(stacks))]
    state = GameState(stacks)
    for i in blocked:
        state.blocked[i] = True
    for i in complete:
        state.complete[i] = True
    return state


class NewGameTest(unittest.TestCase):
    def test_deals_four_of_each_card_into_six_stacks_of_six(self):
        state = new_game(random.Random(0))
        self.assertEqual([len(s) for s in state.stacks], [6] * 6)
        cards = Counter(card for stack in state.stacks for card in stack)
        self.assertEqual(cards, Counter({value: 4 for value in range(1, 10)}))
        self.assertFalse(any(state.blocked) or any(state.complete))

    def test_same_seed_gives_same_deal(self):
        self.assertEqual(new_game(random.Random(42)), new_game(random.Random(42)))


class ParseCommandTest(unittest.TestCase):
    def test_moves(self):
        self.assertEqual(parse_command("AB"), Move(0, 1, 1))
        self.assertEqual(parse_command(" fa3 "), Move(5, 0, 3))

    def test_commands_are_case_insensitive(self):
        self.assertIs(parse_command("u"), Command.UNDO)
        self.assertIs(parse_command("R"), Command.RESET)
        self.assertIs(parse_command("q"), Command.QUIT)

    def test_rejects_malformed_input(self):
        for text in ["", "A", "ABCD", "AZ", "GA", "AB0", "ABx"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_command(text)


class IsValidMoveTest(unittest.TestCase):
    def test_card_fits_on_one_higher(self):
        self.assertTrue(is_valid_move(board([5], [6]), Move(0, 1)))

    def test_any_card_fits_on_empty_stack(self):
        self.assertTrue(is_valid_move(board([5]), Move(0, 3)))

    def test_single_card_may_be_dropped_out_of_sequence(self):
        self.assertTrue(is_valid_move(board([5], [2]), Move(0, 1)))

    def test_nothing_can_land_on_blocked_stack(self):
        self.assertFalse(is_valid_move(board([5], [6], blocked=[1]), Move(0, 1)))

    def test_blocked_card_can_only_move_into_sequence_or_empty(self):
        state = board([9, 4], [5], [7], blocked=[0])
        self.assertTrue(is_valid_move(state, Move(0, 1)))
        self.assertTrue(is_valid_move(state, Move(0, 3)))
        self.assertFalse(is_valid_move(state, Move(0, 2)))

    def test_blocked_stack_gives_up_one_card_at_a_time(self):
        self.assertFalse(is_valid_move(board([5, 4], [], blocked=[0]), Move(0, 1, 2)))

    def test_run_moves_together(self):
        self.assertTrue(is_valid_move(board([1, 6, 5, 4], [7]), Move(0, 1, 3)))
        self.assertTrue(is_valid_move(board([1, 6, 5, 4]), Move(0, 2, 3)))

    def test_run_must_fit_target(self):
        self.assertFalse(is_valid_move(board([6, 5, 4], [9]), Move(0, 1, 3)))

    def test_non_run_cannot_move_together(self):
        self.assertFalse(is_valid_move(board([6, 3, 4]), Move(0, 1, 2)))

    def test_too_many_cards(self):
        self.assertFalse(is_valid_move(board([2, 1]), Move(0, 1, 3)))

    def test_same_stack_and_empty_source(self):
        self.assertFalse(is_valid_move(board([5]), Move(0, 0)))
        self.assertFalse(is_valid_move(board([], [5]), Move(0, 1)))

    def test_complete_stacks_are_locked(self):
        state = board(COMPLETE_RUN, [], complete=[0])
        self.assertFalse(is_valid_move(state, Move(0, 1)))
        self.assertFalse(is_valid_move(board([5], [6], complete=[1]), Move(0, 1)))


class ApplyMoveTest(unittest.TestCase):
    def test_moves_cards_without_mutating_original(self):
        before = board([3, 6, 5], [7])
        after = apply_move(before, Move(0, 1, 2))
        self.assertEqual(after.stacks[:2], [[3], [7, 6, 5]])
        self.assertEqual(before.stacks[:2], [[3, 6, 5], [7]])

    def test_out_of_sequence_drop_blocks_target(self):
        after = apply_move(board([5], [2]), Move(0, 1))
        self.assertTrue(after.blocked[1])

    def test_moving_blocking_card_unblocks_source(self):
        after = apply_move(board([2, 5], [6], blocked=[0]), Move(0, 1))
        self.assertFalse(after.blocked[0])
        self.assertFalse(after.blocked[1])

    def test_full_run_completes_stack(self):
        after = apply_move(board([1], COMPLETE_RUN[:-1]), Move(0, 1))
        self.assertTrue(after.complete[1])


class IsWonTest(unittest.TestCase):
    def test_won_with_four_complete_stacks(self):
        state = board(*[COMPLETE_RUN] * 4, complete=range(4))
        self.assertTrue(is_won(state))

    def test_not_won_with_three(self):
        state = board(*[COMPLETE_RUN] * 3, complete=range(3))
        self.assertFalse(is_won(state))


if __name__ == "__main__":
    unittest.main()
