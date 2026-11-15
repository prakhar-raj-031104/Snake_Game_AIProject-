"""Breadth-First Search (BFS) on the 3D grid.

BFS explores the grid level by level: first every cell 1 step away, then
every cell 2 steps away, and so on. Because of this, the first time it
reaches a cell it has found the SHORTEST path to it.

Nothing here depends on the number of dimensions: the board decides who the
neighbours are (4 in 2D, 6 in 3D) and BFS works the same way.
"""

from collections import deque

from .board import Board
from .geometry import Point

CameFrom = dict[Point, Point | None]


class BFSPathfinder:
    """Finds shortest paths on a board while avoiding blocked cells."""

    def __init__(self, board: Board) -> None:
        self.board = board

    def find_path(self, start: Point, goal: Point,
                  blocked: set[Point]) -> list[Point] | None:
        """Shortest path from `start` to `goal` (excluding `start`), or None."""
        came_from = self._search(start, blocked, goal)
        return self.path_to(came_from, goal)

    def explore(self, start: Point, blocked: set[Point]) -> CameFrom:
        """Run BFS to EVERY reachable cell at once.

        One search answers "how do I get to X?" for all targets, which lets the
        agent compare several pieces of food without searching again.
        """
        return self._search(start, blocked)

    def count_reachable(self, start: Point, blocked: set[Point]) -> int:
        """Count how many free cells can be reached from `start` (flood fill)."""
        if start in blocked or not self.board.is_free(start):
            return 0
        return len(self._search(start, blocked))

    @staticmethod
    def path_to(came_from: CameFrom, goal: Point) -> list[Point] | None:
        """Walk backwards from the goal to the start to recover the path."""
        if goal not in came_from:
            return None
        path = []
        current: Point | None = goal
        while came_from[current] is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def _search(self, start: Point, blocked: set[Point],
                goal: Point | None = None) -> CameFrom:
        """The BFS itself. Stops early if `goal` is given and reached."""
        queue: deque[Point] = deque([start])
        came_from: CameFrom = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                break
            for neighbor in self.board.neighbors(current):
                if neighbor in came_from or neighbor in blocked:
                    continue
                came_from[neighbor] = current
                queue.append(neighbor)

        return came_from
