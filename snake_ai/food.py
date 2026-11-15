"""Food the snake can eat: normal apples and time-limited golden apples."""

import random
from dataclasses import dataclass

from .geometry import Point


@dataclass(frozen=True)
class FoodKind:
    """What kind of food this is and how much it is worth."""

    name: str
    points: int
    lifetime: int | None  # moves before it disappears (None = never)


APPLE = FoodKind("apple", points=1, lifetime=None)
GOLDEN = FoodKind("golden apple", points=5, lifetime=40)


@dataclass
class Food:
    """One piece of food lying on the board."""

    position: Point
    kind: FoodKind
    moves_left: int | None = None

    @classmethod
    def spawn(cls, kind: FoodKind, free_cells: list[Point],
              rng: random.Random) -> "Food | None":
        """Place food of `kind` on a random free cell (None if there is no room)."""
        if not free_cells:
            return None
        return cls(rng.choice(free_cells), kind, kind.lifetime)

    @property
    def points(self) -> int:
        return self.kind.points

    @property
    def expired(self) -> bool:
        return self.moves_left is not None and self.moves_left <= 0

    def tick(self) -> None:
        """One move has passed. Time-limited food gets closer to vanishing."""
        if self.moves_left is not None:
            self.moves_left -= 1
