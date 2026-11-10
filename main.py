"""Entry point.

Run the game with a window:      python main.py
Run without a window (testing):  python main.py --headless --games 10
"""

import argparse

from snake_ai.agent import BFSAgent
from snake_ai.config import GameConfig
from snake_ai.game import SnakeGame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Snake game played by a BFS AI agent.")
    parser.add_argument("--width", type=int, default=20, help="grid columns (default 20)")
    parser.add_argument("--height", type=int, default=20, help="grid rows (default 20)")
    parser.add_argument("--cell-size", type=int, default=30, help="cell size in pixels")
    parser.add_argument("--fps", type=int, default=15, help="moves per second")
    parser.add_argument("--seed", type=int, default=None, help="random seed for repeatable games")
    parser.add_argument("--headless", action="store_true",
                        help="play without a window and print the results")
    parser.add_argument("--games", type=int, default=5,
                        help="number of games to play in headless mode")
    return parser.parse_args()


def run_headless(config: GameConfig, games: int, seed: int | None) -> None:
    """Let the AI play several games quickly and print the scores."""
    scores = []
    for number in range(1, games + 1):
        game_seed = None if seed is None else seed + number
        game = SnakeGame(config.grid_width, config.grid_height, game_seed)
        agent = BFSAgent(game.board)
        max_steps = game.board.total_cells * 200  # safety limit against endless loops

        while not game.is_over and game.steps < max_steps:
            game.step(agent.choose_direction(game.snake, game.food.position))

        scores.append(game.score)
        print(f"Game {number}: score={game.score} length={len(game.snake)} "
              f"steps={game.steps} result={game.status.name}")

    print(f"\nAverage score: {sum(scores) / len(scores):.1f}   Best score: {max(scores)}")


def main() -> None:
    args = parse_args()
    config = GameConfig(grid_width=args.width, grid_height=args.height,
                        cell_size=args.cell_size, fps=args.fps)

    if args.headless:
        run_headless(config, max(1, args.games), args.seed)
    else:
        from snake_ai.app import SnakeApp  # imported here so headless mode needs no display
        SnakeApp(config, args.seed).run()


if __name__ == "__main__":
    main()
