"""Command-line game loop: read moves, keep undo history, redraw the board."""

from __future__ import annotations

import argparse
import random

from .display import CLEAR_SCREEN, render_board
from .game import Command, GameState, apply_move, is_valid_move, is_won, new_game, parse_command

HELP_TEXT = """\
Goal: build four stacks running 9 down to 1.

Moves:  AB    move the top card of stack A onto stack B
        AB3   move the top 3 cards of A onto B (they must run downwards, e.g. 6 5 4)
Other:  U undo   R new game   H help   Q quit

A card fits on a card one higher, or on an empty stack. You may also drop a
single card anywhere, but that stack is then blocked (shown in grey) until
you move that card away."""


def play(rng: random.Random | None = None) -> None:
    history: list[GameState] = [new_game(rng)]
    message = "Type H for help."

    while True:
        board = history[-1]
        print(CLEAR_SCREEN + render_board(board) + "\n")

        if is_won(board):
            print("You won! Every card is in order.")
            return

        print(message)
        try:
            text = input("Your move: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            action = parse_command(text)
        except ValueError as error:
            message = str(error)
            continue

        if action is Command.QUIT:
            return
        elif action is Command.HELP:
            message = HELP_TEXT
        elif action is Command.RESET:
            history = [new_game(rng)]
            message = "New game dealt."
        elif action is Command.UNDO:
            if len(history) > 1:
                history.pop()
                message = "Move undone."
            else:
                message = "Nothing to undo."
        elif is_valid_move(board, action):
            history.append(apply_move(board, action))
            message = ""
        else:
            message = "That move isn't allowed. Type H for the rules."


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Play a terminal solitaire game.")
    parser.add_argument("--seed", type=int, help="deal a repeatable game from this seed")
    args = parser.parse_args(argv)
    play(random.Random(args.seed))


if __name__ == "__main__":
    main()
