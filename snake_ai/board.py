"""The game board: a rectangular grid of cells."""

from collections.abc import Iterator

from .geometry import Direction, Point


class Board:
    """Knows the size of the grid and which cells are neighbours."""

    def __init__(self, width: int, height: int) -> None:
        if width < 4 or height < 4:
            raise ValueError("Board must be at least 4x4 cells.")
        self.width = width
        self.height = height

    @property
    def total_cells(self) -> int:
        return self.width * self.height

    @property
    def center(self) -> Point:
        return Point(self.width // 2, self.height // 2)

    def contains(self, point: Point) -> bool:
        """True if the point is inside the walls."""
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def neighbors(self, point: Point) -> Iterator[Point]:
        """Yield the (up to four) cells next to `point` that are on the board."""
        for direction in Direction:
            neighbor = point + direction.value
            if self.contains(neighbor):
                yield neighbor

    def all_cells(self) -> Iterator[Point]:
        for y in range(self.height):
            for x in range(self.width):
                yield Point(x, y)
