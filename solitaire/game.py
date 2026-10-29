"""Core game rules: dealing, parsing input, validating and applying moves.

Everything here is pure logic with no printing or input, so it can be
unit-tested and reused by any front end.
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple

STACK_LABELS = "ABCDEF"
NUM_STACKS = len(STACK_LABELS)
HIGHEST_CARD = 9
COPIES_PER_CARD = 4
CARDS_PER_STACK = HIGHEST_CARD * COPIES_PER_CARD // NUM_STACKS

# A stack is complete once it holds a full run from 9 down to 1.
COMPLETE_RUN = list(range(HIGHEST_CARD, 0, -1))
STACKS_TO_WIN = COPIES_PER_CARD


@dataclass
class GameState:
    """The board: six stacks of cards plus a status flag for each stack.

    ``stacks[i]`` is ordered bottom to top, so ``stacks[i][-1]`` is the
    playable card. A stack is *blocked* when a card was placed on it out of
    sequence, and *complete* when it holds a full 9-to-1 run.
    """

    stacks: list[list[int]]
    blocked: list[bool] = field(default_factory=lambda: [False] * NUM_STACKS)
    complete: list[bool] = field(default_factory=lambda: [False] * NUM_STACKS)

    def copy(self) -> GameState:
        return copy.deepcopy(self)


class Move(NamedTuple):
    source: int
    destination: int
    count: int = 1


class Command(Enum):
    UNDO = "U"
    RESET = "R"
    HELP = "H"
    QUIT = "Q"


def new_game(rng: random.Random | None = None) -> GameState:
    """Shuffle four copies of the cards 1-9 and deal them into six stacks."""
    rng = rng or random.Random()
    deck = list(range(1, HIGHEST_CARD + 1)) * COPIES_PER_CARD
    rng.shuffle(deck)
    stacks = [
        deck[i * CARDS_PER_STACK:(i + 1) * CARDS_PER_STACK]
        for i in range(NUM_STACKS)
    ]
    return GameState(stacks)


def parse_command(text: str) -> Move | Command:
    """Turn user input such as ``"AB"``, ``"cd3"`` or ``"u"`` into a move or command.

    Raises ``ValueError`` with a user-facing message if the input is malformed.
    """
    text = text.strip().upper()

    for command in Command:
        if text == command.value:
            return command

    if not 2 <= len(text) <= 3:
        raise ValueError("Enter a move like AB or AB3, or H for help.")

    source, destination = text[0], text[1]
    if source not in STACK_LABELS or destination not in STACK_LABELS:
        raise ValueError(f"Stacks must be letters {STACK_LABELS[0]}-{STACK_LABELS[-1]}.")

    count = 1
    if len(text) == 3:
        if not text[2].isdigit() or text[2] == "0":
            raise ValueError(f"Number of cards must be 1-{HIGHEST_CARD}.")
        count = int(text[2])

    return Move(STACK_LABELS.index(source), STACK_LABELS.index(destination), count)


def _is_descending_run(cards: list[int]) -> bool:
    return all(upper == lower + 1 for upper, lower in zip(cards, cards[1:]))


def is_valid_move(state: GameState, move: Move) -> bool:
    """Check a move against the rules without changing the board.

    - Cards can't be taken from, or placed on, a complete stack.
    - Nothing can be placed on a blocked stack.
    - Any card(s) may go onto an empty stack.
    - A card (or the bottom card of a moved run) fits onto a card one higher.
    - Several cards can only move together if they form a descending run.
    - A single card from an unblocked stack may also be placed out of
      sequence, but this blocks the stack it lands on.
    - A blocked stack can only give up its top card.
    """
    source, destination, count = move
    if source == destination:
        return False
    if not (0 <= source < NUM_STACKS and 0 <= destination < NUM_STACKS):
        return False
    if state.complete[source] or state.complete[destination]:
        return False
    if state.blocked[destination]:
        return False

    source_stack = state.stacks[source]
    target_stack = state.stacks[destination]
    if not 1 <= count <= len(source_stack):
        return False

    cards = source_stack[-count:]
    if count > 1 and (state.blocked[source] or not _is_descending_run(cards)):
        return False

    if not target_stack or cards[0] == target_stack[-1] - 1:
        return True

    return count == 1 and not state.blocked[source]


def apply_move(state: GameState, move: Move) -> GameState:
    """Return the board after ``move``. The given state is left unchanged.

    Assumes the move has already passed ``is_valid_move``.
    """
    new_state = state.copy()
    source, destination, count = move

    cards = new_state.stacks[source][-count:]
    del new_state.stacks[source][-count:]
    target = new_state.stacks[destination]
    target.extend(cards)

    # Moving the top card off a blocked stack removes whatever blocked it.
    new_state.blocked[source] = False
    new_state.blocked[destination] = len(target) > 1 and target[-1] != target[-2] - 1
    new_state.complete[destination] = target == COMPLETE_RUN
    return new_state


def is_won(state: GameState) -> bool:
    """The game is won once four stacks are complete, i.e. every card is sorted."""
    return sum(state.complete) == STACKS_TO_WIN
