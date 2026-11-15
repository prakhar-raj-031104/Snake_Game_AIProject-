"""Basic building blocks: a 3D grid position and the six move directions."""

from enum import Enum
from typing import NamedTuple


class Point(NamedTuple):
    """A cell in the 3D grid.

    x = left/right, y = back/forward, z = down/up.
    `z` defaults to 0, so 2D code can still write Point(x, y).
    """

    x: int
    y: int
    z: int = 0

    def __add__(self, other: "Point") -> "Point":  # type: ignore[override]
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def scaled(self, factor: int) -> "Point":
        return Point(self.x * factor, self.y * factor, self.z * factor)


class Direction(Enum):
    """The six directions the snake can move in a 3D world."""

    RIGHT = Point(1, 0, 0)
    LEFT = Point(-1, 0, 0)
    FORWARD = Point(0, 1, 0)
    BACKWARD = Point(0, -1, 0)
    UP = Point(0, 0, 1)
    DOWN = Point(0, 0, -1)

    @property
    def opposite(self) -> "Direction":
        return Direction(self.value.scaled(-1))

    @staticmethod
    def between(start: Point, end: Point) -> "Direction":
        """Return the direction that moves from `start` to the adjacent `end`."""
        return Direction(Point(end.x - start.x, end.y - start.y, end.z - start.z))
