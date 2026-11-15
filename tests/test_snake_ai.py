"""Unit tests for the game logic and the BFS agent (no window needed)."""

from snake_ai.agent import BFSAgent
from snake_ai.board import Board
from snake_ai.food import APPLE, GOLDEN, Food
from snake_ai.game import GameStatus, SnakeGame
from snake_ai.geometry import Direction, Point
from snake_ai.pathfinder import BFSPathfinder
from snake_ai.snake import Snake


# ----- Geometry and board ----------------------------------------------------

def test_directions_have_opposites():
    assert Direction.UP.opposite == Direction.DOWN
    assert Direction.LEFT.opposite == Direction.RIGHT
    assert Direction.between(Point(1, 1, 1), Point(1, 1, 2)) == Direction.UP


def test_board_has_six_neighbours_in_3d():
    board = Board(5, 5, 5)
    assert len(list(board.neighbors(Point(2, 2, 2)))) == 6
    assert len(list(board.neighbors(Point(0, 0, 0)))) == 3   # a corner


def test_flat_board_behaves_like_2d():
    board = Board(5, 5, 1)
    assert len(list(board.neighbors(Point(2, 2, 0)))) == 4


def test_rocks_block_cells():
    board = Board(5, 5, 5)
    board.rocks.add(Point(2, 2, 3))
    assert not board.is_free(Point(2, 2, 3))
    assert Point(2, 2, 3) not in set(board.neighbors(Point(2, 2, 2)))


# ----- BFS pathfinder ------------------------------------------------------

def test_bfs_finds_shortest_path_in_3d():
    finder = BFSPathfinder(Board(6, 6, 6))
    path = finder.find_path(Point(0, 0, 0), Point(2, 3, 4), blocked=set())
    assert path is not None
    assert len(path) == 9          # 2 + 3 + 4 steps
    assert path[-1] == Point(2, 3, 4)


def test_bfs_climbs_over_a_wall():
    # A wall fills the whole x=2 slice except the top layer: BFS must go up and over.
    board = Board(5, 5, 3)
    wall = {Point(2, y, z) for y in range(5) for z in range(2)}
    path = BFSPathfinder(board).find_path(Point(0, 0, 0), Point(4, 0, 0), blocked=wall)
    assert path is not None
    assert not set(path) & wall
    assert any(cell.z == 2 for cell in path)
    assert len(path) == 8          # 4 across + 2 up + 2 down


def test_bfs_returns_none_when_unreachable():
    board = Board(5, 5, 2)
    wall = {Point(2, y, z) for y in range(5) for z in range(2)}
    assert BFSPathfinder(board).find_path(Point(0, 0, 0), Point(4, 4, 1), blocked=wall) is None


def test_explore_reaches_every_cell():
    board = Board(4, 4, 4)
    came_from = BFSPathfinder(board).explore(Point(0, 0, 0), blocked=set())
    assert len(came_from) == 64


# ----- Snake and food --------------------------------------------------------

def test_snake_moves_and_grows():
    snake = Snake(Point(5, 5, 5), length=3)
    assert snake.body == [Point(5, 5, 5), Point(4, 5, 5), Point(3, 5, 5)]
    snake.turn(Direction.UP)
    snake.move()
    assert snake.head == Point(5, 5, 6) and len(snake) == 3
    snake.move(grow=True)
    assert snake.head == Point(5, 5, 7) and len(snake) == 4


def test_snake_cannot_reverse():
    snake = Snake(Point(5, 5, 5), direction=Direction.RIGHT)
    snake.turn(Direction.LEFT)
    assert snake.direction == Direction.RIGHT


def test_golden_apple_expires():
    food = Food(Point(0, 0, 0), GOLDEN, moves_left=2)
    food.tick()
    assert not food.expired
    food.tick()
    assert food.expired


# ----- Game rules ----------------------------------------------------------

def test_hitting_wall_ends_game():
    game = SnakeGame(6, 6, 6, rock_ratio=0, seed=1)
    game.foods = [Food(Point(0, 0, 0), APPLE)]  # keep food out of the way
    for _ in range(10):
        game.step(Direction.RIGHT)
    assert game.status == GameStatus.GAME_OVER


def test_hitting_rock_ends_game():
    game = SnakeGame(8, 8, 8, rock_ratio=0, seed=1)
    game.foods = [Food(Point(0, 0, 0), APPLE)]
    game.board.rocks.add(game.snake.next_head(Direction.UP))
    game.step(Direction.UP)
    assert game.status == GameStatus.GAME_OVER


def test_eating_golden_apple_gives_bonus():
    game = SnakeGame(8, 8, 8, rock_ratio=0, seed=1)
    target = game.snake.next_head(Direction.RIGHT)
    game.foods = [Food(target, GOLDEN, GOLDEN.lifetime)]
    game.step(Direction.RIGHT)
    assert game.score == GOLDEN.points
    assert game.golden_eaten == 1
    assert len(game.snake) == 4


def test_rocks_never_seal_off_space():
    for seed in range(5):
        game = SnakeGame(6, 6, 6, rock_ratio=0.15, seed=seed)
        reachable = BFSPathfinder(game.board).count_reachable(game.snake.head, set())
        assert reachable == game.board.free_cell_count
        assert len(game.board.rocks) > 0


# ----- Agent ---------------------------------------------------------------

def test_agent_moves_up_towards_food():
    board = Board(10, 10, 10)
    agent = BFSAgent(board)
    snake = Snake(Point(5, 5, 5), direction=Direction.RIGHT)
    assert agent.choose_direction(snake, [Food(Point(5, 5, 9), APPLE)]) == Direction.UP


def test_agent_prefers_golden_apple_when_worth_it():
    board = Board(10, 10, 10)
    agent = BFSAgent(board)
    snake = Snake(Point(5, 5, 5), direction=Direction.RIGHT)
    apple = Food(Point(8, 5, 5), APPLE)                  # 3 moves for 1 point
    golden = Food(Point(5, 5, 9), GOLDEN, 40)            # 4 moves for 5 points
    assert agent.choose_direction(snake, [apple, golden]) == Direction.UP


def test_agent_skips_golden_apple_it_cannot_reach_in_time():
    board = Board(10, 10, 10)
    agent = BFSAgent(board)
    snake = Snake(Point(5, 5, 5), direction=Direction.RIGHT)
    apple = Food(Point(8, 5, 5), APPLE)
    golden = Food(Point(5, 5, 9), GOLDEN, moves_left=2)  # vanishes before we arrive
    assert agent.choose_direction(snake, [apple, golden]) == Direction.RIGHT


def test_agent_scores_well_in_3d():
    for seed in range(3):
        game = SnakeGame(6, 6, 6, seed=seed)
        agent = BFSAgent(game.board)
        while not game.is_over and game.steps < 20_000:
            game.step(agent.choose_direction(game.snake, game.foods))
        assert game.score >= 30


def test_agent_still_plays_classic_2d():
    game = SnakeGame(10, 10, 1, rock_ratio=0, seed=3)
    agent = BFSAgent(game.board)
    while not game.is_over and game.steps < 20_000:
        game.step(agent.choose_direction(game.snake, game.foods))
    assert game.score >= 20
