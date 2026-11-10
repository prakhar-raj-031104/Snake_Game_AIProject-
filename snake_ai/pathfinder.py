"""Breadth-First Search (BFS) on the game grid.

BFS explores the grid level by level: first every cell 1 step away, then
every cell 2 steps away, and so on. Because of this, the first time it
reaches the goal it has found the SHORTEST path.
"""

from collections import deque

from .board import Board
from .geometry import Point


class BFSPathfinder:
    """Finds shortest paths on a board while avoiding blocked cells."""

    def __init__(self, board: Board) -> None:
        self.board = board

    def find_path(self, start: Point, goal: Point,
                  blocked: set[Point]) -> list[Point] | None:
        """Return the shortest path from `start` to `goal` (excluding `start`).

        Returns None when the goal cannot be reached.
        """
        queue: deque[Point] = deque([start])
        came_from: dict[Point, Point | None] = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                return self._rebuild_path(came_from, goal)

            for neighbor in self.board.neighbors(current):
                if neighbor in came_from or neighbor in blocked:
                    continue
                came_from[neighbor] = current
                queue.append(neighbor)

        return None

    def count_reachable(self, start: Point, blocked: set[Point]) -> int:
        """Count how many free cells can be reached from `start` (flood fill)."""
        if start in blocked or not self.board.contains(start):
            return 0
        queue: deque[Point] = deque([start])
        visited = {start}
        while queue:
            current = queue.popleft()
            for neighbor in self.board.neighbors(current):
                if neighbor not in visited and neighbor not in blocked:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return len(visited)

    @staticmethod
    def _rebuild_path(came_from: dict[Point, Point | None], goal: Point) -> list[Point]:
        """Walk backwards from the goal to the start to recover the path."""
        path = []
        current: Point | None = goal
        while came_from[current] is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
