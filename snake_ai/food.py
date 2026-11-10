"""The food the snake is trying to eat."""

import random

from .board import Board
from .geometry import Point
from .snake import Snake


class Food:
    """Places food on a random empty cell."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()
        self.position: Point | None = None

    def respawn(self, board: Board, snake: Snake) -> bool:
        """Move the food to a free cell. Returns False if the board is full."""
        free_cells = [cell for cell in board.all_cells() if not snake.occupies(cell)]
        if not free_cells:
            self.position = None
            return False
        self.position = self._rng.choice(free_cells)
        return True
