"""Pure game rules. No graphics here, so the logic is easy to test."""

import random
from enum import Enum, auto

from .board import Board
from .food import APPLE, GOLDEN, Food, FoodKind
from .geometry import Direction, Point
from .pathfinder import BFSPathfinder
from .snake import Snake


class GameStatus(Enum):
    RUNNING = auto()
    GAME_OVER = auto()
    WON = auto()


class SnakeGame:
    """Holds the world, snake and food, and applies one move at a time.

    Rules:
      * The snake moves in 3D: left/right, forward/back and up/down.
      * Hitting a wall, a rock or itself ends the game.
      * There is always one apple (+1). After an apple is eaten, a golden
        apple (+5) may appear. It vanishes if not eaten in time.
    """

    def __init__(self, width: int = 10, depth: int = 10, height: int = 10,
                 rock_ratio: float = 0.03, golden_chance: float = 0.3,
                 seed: int | None = None) -> None:
        self.board = Board(width, depth, height)
        self.rock_ratio = rock_ratio
        self.golden_chance = golden_chance
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        """Start a fresh game with new rocks."""
        self.snake = Snake(self.board.center)
        self._place_rocks()
        self.foods: list[Food] = []
        self._spawn(APPLE)
        self.score = 0
        self.golden_eaten = 0
        self.steps = 0
        self.status = GameStatus.RUNNING

    @property
    def is_over(self) -> bool:
        return self.status != GameStatus.RUNNING

    @property
    def golden_apple(self) -> Food | None:
        return next((food for food in self.foods if food.kind is GOLDEN), None)

    def step(self, direction: Direction) -> GameStatus:
        """Move the snake once and update score / status."""
        if self.is_over:
            return self.status

        self.snake.turn(direction)
        eaten = self._food_at(self.snake.next_head(self.snake.direction))

        self.snake.move(grow=eaten is not None)
        self.steps += 1

        if not self.board.is_free(self.snake.head) or self.snake.hits_itself():
            self.status = GameStatus.GAME_OVER
            return self.status

        if eaten:
            self._eat(eaten)
        self._age_foods()
        return self.status

    # ----- helpers -------------------------------------------------------

    def _food_at(self, cell: Point) -> Food | None:
        return next((food for food in self.foods if food.position == cell), None)

    def _eat(self, food: Food) -> None:
        self.score += food.points
        self.foods.remove(food)
        if food.kind is GOLDEN:
            self.golden_eaten += 1
            return
        if not self._spawn(APPLE):
            self.status = GameStatus.WON  # no room left: the snake fills the world
        elif self.golden_apple is None and self._rng.random() < self.golden_chance:
            self._spawn(GOLDEN)

    def _age_foods(self) -> None:
        """Golden apples count down and disappear when their time is up."""
        for food in self.foods:
            food.tick()
        self.foods = [food for food in self.foods if not food.expired]

    def _spawn(self, kind: FoodKind) -> bool:
        taken = {food.position for food in self.foods}
        free = [cell for cell in self.board.free_cells()
                if not self.snake.occupies(cell) and cell not in taken]
        food = Food.spawn(kind, free, self._rng)
        if food is None:
            return False
        self.foods.append(food)
        return True

    def _place_rocks(self) -> None:
        """Scatter rocks, but never seal off part of the world."""
        self.board.rocks.clear()
        count = int(self.board.total_cells * self.rock_ratio)
        if count == 0:
            return

        # Keep the snake and the cells in front of it clear.
        keep_clear = set(self.snake.body)
        keep_clear |= {self.snake.next_head(self.snake.direction) +
                       self.snake.direction.value.scaled(i) for i in range(3)}

        candidates = [cell for cell in self.board.all_cells() if cell not in keep_clear]
        self._rng.shuffle(candidates)
        pathfinder = BFSPathfinder(self.board)

        for cell in candidates:
            if len(self.board.rocks) == count:
                break
            self.board.rocks.add(cell)
            # A rock may stay only if every free cell is still reachable.
            reachable = pathfinder.count_reachable(self.snake.head, set())
            if reachable != self.board.free_cell_count:
                self.board.rocks.discard(cell)
