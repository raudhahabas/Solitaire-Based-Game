"""Render the board as coloured text using 24-bit ANSI escape codes."""

from __future__ import annotations

from .game import STACK_LABELS, GameState

RESET = "\033[0m"
CLEAR_SCREEN = "\033[2J\033[H"

# One colour per card value, 1 (red) through 9 (purple), as RGB in 0-1.
CARD_COLOURS = [
    (1.0, 0.349, 0.369), (1.0, 0.573, 0.298), (1.0, 0.792, 0.227),
    (0.773, 0.792, 0.188), (0.541, 0.788, 0.149), (0.322, 0.651, 0.459),
    (0.098, 0.509, 0.769), (0.259, 0.404, 0.675), (0.416, 0.298, 0.576),
]

Rgb = tuple[float, float, float]


def _rgb(r: float, g: float, b: float) -> str:
    return f"{int(r * 255)};{int(g * 255)};{int(b * 255)}"


def card_colours(value: int) -> tuple[Rgb, Rgb]:
    """Foreground (pale tint) and background (darker shade) for a card value."""
    r, g, b = CARD_COLOURS[value - 1]
    foreground = ((r + 2) / 3, (g + 2) / 3, (b + 2) / 3)
    background = (r / 1.5, g / 1.5, b / 1.5)
    return foreground, background


def colour_text(text: str, foreground: Rgb, background: Rgb) -> str:
    return f"\033[38;2;{_rgb(*foreground)}m\033[48;2;{_rgb(*background)}m{text}{RESET}"


BLOCKED_COLOURS: tuple[Rgb, Rgb] = ((0.2, 0.2, 0.2), (0.8, 0.8, 0.8))


def render_card(state: GameState, stack: int, row: int) -> str:
    """Return the 3-character cell for one card, or blank space if there is none."""
    cards = state.stacks[stack]
    if row >= len(cards):
        return "   "

    value = cards[row]
    is_top = row == len(cards) - 1
    if is_top and state.blocked[stack]:
        return colour_text(f" {value} ", *BLOCKED_COLOURS)
    if state.complete[stack]:
        return colour_text("   ", *card_colours(value))
    return colour_text(f" {value} ", *card_colours(value))


def render_board(state: GameState) -> str:
    """Draw the stacks side by side, growing up from the labels, so each
    stack's playable card is the highest one in its column."""
    height = max((len(stack) for stack in state.stacks), default=0)
    lines = []
    for row in range(height - 1, -1, -1):
        cells = [render_card(state, i, row) for i in range(len(state.stacks))]
        lines.append(" ".join(cells).rstrip())
    lines.append(" ".join(f" {label} " for label in STACK_LABELS).rstrip())
    return "\n".join(lines)
