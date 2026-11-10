"""Basic building blocks: a grid position and the four move directions."""

from enum import Enum
from typing import NamedTuple


class Point(NamedTuple):
    """A cell on the grid. x is the column, y is the row."""

    x: int
    y: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)


class Direction(Enum):
    """The four directions the snake can move in."""

    UP = Point(0, -1)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)

    @property
    def opposite(self) -> "Direction":
        return _OPPOSITES[self]

    @staticmethod
    def between(start: Point, end: Point) -> "Direction":
        """Return the direction that moves from `start` to the adjacent `end`."""
        delta = Point(end.x - start.x, end.y - start.y)
        return Direction(delta)


_OPPOSITES = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}
