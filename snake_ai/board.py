"""The game world: a 3D box of cells, with some cells blocked by rocks."""

from collections.abc import Iterator

from .geometry import Direction, Point


class Board:
    """Knows the size of the world, where the rocks are, and which cells touch."""

    def __init__(self, width: int, depth: int, height: int = 1) -> None:
        if width < 4 or depth < 4 or height < 1:
            raise ValueError("Board must be at least 4 x 4 x 1 cells.")
        self.width = width    # x
        self.depth = depth    # y
        self.height = height  # z (height 1 = classic flat Snake)
        self.rocks: set[Point] = set()

    @property
    def total_cells(self) -> int:
        return self.width * self.depth * self.height

    @property
    def free_cell_count(self) -> int:
        return self.total_cells - len(self.rocks)

    @property
    def center(self) -> Point:
        return Point(self.width // 2, self.depth // 2, self.height // 2)

    def contains(self, point: Point) -> bool:
        """True if the point is inside the walls."""
        return (0 <= point.x < self.width
                and 0 <= point.y < self.depth
                and 0 <= point.z < self.height)

    def is_free(self, point: Point) -> bool:
        """True if the snake may enter this cell (inside the walls, no rock)."""
        return self.contains(point) and point not in self.rocks

    def neighbors(self, point: Point) -> Iterator[Point]:
        """Yield the free cells next to `point` (up to six in 3D)."""
        for direction in Direction:
            neighbor = point + direction.value
            if self.is_free(neighbor):
                yield neighbor

    def all_cells(self) -> Iterator[Point]:
        for z in range(self.height):
            for y in range(self.depth):
                for x in range(self.width):
                    yield Point(x, y, z)

    def free_cells(self) -> Iterator[Point]:
        return (cell for cell in self.all_cells() if cell not in self.rocks)
