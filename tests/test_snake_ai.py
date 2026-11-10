"""Unit tests for the game logic and the BFS agent (no window needed)."""

from snake_ai.agent import BFSAgent
from snake_ai.board import Board
from snake_ai.game import GameStatus, SnakeGame
from snake_ai.geometry import Direction, Point
from snake_ai.pathfinder import BFSPathfinder
from snake_ai.snake import Snake


# ----- BFS pathfinder ------------------------------------------------------

def test_bfs_finds_shortest_path_on_empty_board():
    finder = BFSPathfinder(Board(10, 10))
    path = finder.find_path(Point(0, 0), Point(3, 4), blocked=set())
    assert path is not None
    assert len(path) == 7          # Manhattan distance 3 + 4
    assert path[-1] == Point(3, 4)


def test_bfs_goes_around_obstacles():
    finder = BFSPathfinder(Board(5, 5))
    wall = {Point(2, 0), Point(2, 1), Point(2, 2), Point(2, 3)}
    path = finder.find_path(Point(0, 0), Point(4, 0), blocked=wall)
    assert path is not None
    assert not set(path) & wall
    assert len(path) == 12         # must go down to row 4 and back up


def test_bfs_returns_none_when_unreachable():
    finder = BFSPathfinder(Board(5, 5))
    wall = {Point(2, y) for y in range(5)}
    assert finder.find_path(Point(0, 0), Point(4, 4), blocked=wall) is None


def test_count_reachable():
    finder = BFSPathfinder(Board(5, 5))
    wall = {Point(2, y) for y in range(5)}
    assert finder.count_reachable(Point(0, 0), wall) == 10


# ----- Snake ---------------------------------------------------------------

def test_snake_moves_and_grows():
    snake = Snake(Point(5, 5), length=3)
    assert snake.body == [Point(5, 5), Point(4, 5), Point(3, 5)]

    snake.move()
    assert snake.head == Point(6, 5) and len(snake) == 3

    snake.move(grow=True)
    assert snake.head == Point(7, 5) and len(snake) == 4


def test_snake_cannot_reverse():
    snake = Snake(Point(5, 5), direction=Direction.RIGHT)
    snake.turn(Direction.LEFT)
    assert snake.direction == Direction.RIGHT


# ----- Game rules ----------------------------------------------------------

def test_hitting_wall_ends_game():
    game = SnakeGame(6, 6, seed=1)
    game.food.position = Point(0, 0)  # keep food out of the way
    for _ in range(10):
        game.step(Direction.RIGHT)
    assert game.status == GameStatus.GAME_OVER


def test_eating_food_increases_score():
    game = SnakeGame(10, 10, seed=1)
    game.food.position = game.snake.next_head(Direction.RIGHT)
    game.step(Direction.RIGHT)
    assert game.score == 1
    assert len(game.snake) == 4


# ----- Agent ---------------------------------------------------------------

def test_agent_moves_towards_food():
    board = Board(10, 10)
    agent = BFSAgent(board)
    snake = Snake(Point(5, 5), direction=Direction.RIGHT)
    assert agent.choose_direction(snake, Point(8, 5)) == Direction.RIGHT
    assert agent.choose_direction(snake, Point(5, 1)) == Direction.UP


def test_agent_scores_well_over_full_games():
    for seed in range(5):
        game = SnakeGame(10, 10, seed=seed)
        agent = BFSAgent(game.board)
        while not game.is_over and game.steps < 20_000:
            game.step(agent.choose_direction(game.snake, game.food.position))
        assert game.score >= 10
