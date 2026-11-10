"""The snake: a chain of cells that moves and grows."""

from collections import deque

from .geometry import Direction, Point


class Snake:
    """Stores the snake's body. The first element is the head."""

    def __init__(self, start: Point, length: int = 3,
                 direction: Direction = Direction.RIGHT) -> None:
        self.direction = direction
        # Build the body behind the head, opposite to the moving direction.
        back = direction.opposite.value
        self._body: deque[Point] = deque(
            Point(start.x + back.x * i, start.y + back.y * i) for i in range(length)
        )
        self._cells: set[Point] = set(self._body)  # fast "is this cell snake?" lookup

    @property
    def head(self) -> Point:
        return self._body[0]

    @property
    def tail(self) -> Point:
        return self._body[-1]

    @property
    def body(self) -> list[Point]:
        return list(self._body)

    def __len__(self) -> int:
        return len(self._body)

    def occupies(self, point: Point) -> bool:
        return point in self._cells

    def next_head(self, direction: Direction) -> Point:
        """Where the head would be after moving in `direction`."""
        return self.head + direction.value

    def turn(self, direction: Direction) -> None:
        """Change direction. A snake cannot reverse straight into its own body."""
        if len(self) > 1 and direction == self.direction.opposite:
            return
        self.direction = direction

    def move(self, grow: bool = False) -> None:
        """Move one step forward. If `grow` is True the tail stays (snake gets longer)."""
        new_head = self.next_head(self.direction)
        if not grow:
            self._cells.discard(self._body.pop())
        self._body.appendleft(new_head)
        self._cells.add(new_head)

    def hits_itself(self) -> bool:
        """True if the head overlaps any other body part."""
        return self.head in list(self._body)[1:]
