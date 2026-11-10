"""The AI player that decides where the snake should move next."""

from .board import Board
from .geometry import Direction, Point
from .pathfinder import BFSPathfinder
from .snake import Snake


class BFSAgent:
    """Chooses moves using Breadth-First Search.

    Every turn the agent tries these plans in order:
      1. FOOD:   BFS for the shortest path from the head to the food, treating
                 the snake's body as obstacles. Only take it if it is "safe":
                 after eating, the snake must still be able to reach its tail
                 (so it can never trap itself in a closed area).
      2. TAIL:   If the food is not safely reachable, BFS to the tail and
                 follow it. Chasing the tail buys time until the food opens up.
      3. SPACE:  Last resort - take the move that leaves the most free cells.

    To avoid circling forever, the agent has a "patience" limit: if it goes
    too many moves without eating, it takes the food path even if it is risky.
    """

    def __init__(self, board: Board) -> None:
        self.board = board
        self.pathfinder = BFSPathfinder(board)
        self.current_path: list[Point] = []  # kept so the renderer can draw it
        self.patience = board.total_cells * 2
        self._moves_without_food = 0
        self._last_length = 0

    def choose_direction(self, snake: Snake, food: Point | None) -> Direction:
        body = snake.body
        self._update_hunger(len(body))

        # Plan 1: shortest path to the food, if it is safe (or we are too hungry).
        if food is not None:
            path = self.pathfinder.find_path(snake.head, food, self._obstacles(body))
            if path and (self._is_safe(body, path) or self._is_impatient):
                return self._follow(snake, path)

        # Plan 2: follow the tail.
        if len(body) > 3:
            path = self.pathfinder.find_path(snake.head, snake.tail, set(body[1:-1]))
            if path:
                return self._follow(snake, path)

        # Plan 3: move into the biggest open area.
        self.current_path = []
        return self._safest_direction(snake)

    # ----- helpers -------------------------------------------------------

    def _update_hunger(self, length: int) -> None:
        """Count moves since the snake last grew."""
        if length != self._last_length:  # grew (or a new game started)
            self._moves_without_food = 0
        else:
            self._moves_without_food += 1
        self._last_length = length

    @property
    def _is_impatient(self) -> bool:
        return self._moves_without_food > self.patience

    def _follow(self, snake: Snake, path: list[Point]) -> Direction:
        self.current_path = path
        return Direction.between(snake.head, path[0])

    @staticmethod
    def _obstacles(body: list[Point]) -> set[Point]:
        """Body cells to avoid. The tail is left out: it moves away next step."""
        return set(body[:-1])

    def _is_safe(self, body: list[Point], path: list[Point]) -> bool:
        """Simulate eating the food, then check the head can still reach the tail."""
        future_body = (path[::-1] + body)[: len(body) + 1]  # grew by one
        if len(future_body) >= self.board.total_cells:
            return True  # the board is full: this is the winning move
        head, tail = future_body[0], future_body[-1]
        return self.pathfinder.find_path(head, tail, set(future_body[1:-1])) is not None

    def _safest_direction(self, snake: Snake) -> Direction:
        """Pick the move that keeps the most free space reachable."""
        obstacles = self._obstacles(snake.body)
        best_direction = snake.direction
        best_space = -1

        for direction in Direction:
            if direction == snake.direction.opposite:
                continue
            next_cell = snake.next_head(direction)
            if not self.board.contains(next_cell) or next_cell in obstacles:
                continue
            space = self.pathfinder.count_reachable(next_cell, obstacles)
            if space > best_space:
                best_direction, best_space = direction, space

        return best_direction
