"""Pure game rules. No graphics here, so the logic is easy to test."""

import random
from enum import Enum, auto

from .board import Board
from .food import Food
from .geometry import Direction
from .snake import Snake


class GameStatus(Enum):
    RUNNING = auto()
    GAME_OVER = auto()
    WON = auto()


class SnakeGame:
    """Holds the board, snake and food, and applies one move at a time."""

    def __init__(self, width: int, height: int, seed: int | None = None) -> None:
        self.board = Board(width, height)
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        """Start a fresh game."""
        self.snake = Snake(self.board.center)
        self.food = Food(self._rng)
        self.food.respawn(self.board, self.snake)
        self.score = 0
        self.steps = 0
        self.status = GameStatus.RUNNING

    @property
    def is_over(self) -> bool:
        return self.status != GameStatus.RUNNING

    def step(self, direction: Direction) -> GameStatus:
        """Move the snake once and update score / status."""
        if self.is_over:
            return self.status

        self.snake.turn(direction)
        will_eat = self.snake.next_head(self.snake.direction) == self.food.position

        self.snake.move(grow=will_eat)
        self.steps += 1

        if not self.board.contains(self.snake.head) or self.snake.hits_itself():
            self.status = GameStatus.GAME_OVER
        elif will_eat:
            self.score += 1
            if not self.food.respawn(self.board, self.snake):
                self.status = GameStatus.WON

        return self.status
