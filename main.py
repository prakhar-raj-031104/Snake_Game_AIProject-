"""Entry point.

Play in 3D:                        python main.py
Classic flat 2D Snake:             python main.py --height 1
Benchmark without a window:        python main.py --headless --games 5
"""

import argparse

from snake_ai.agent import BFSAgent
from snake_ai.config import GameConfig
from snake_ai.game import SnakeGame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="3D Snake game played by a BFS AI agent.")
    parser.add_argument("--width", type=int, default=10, help="cells left-right (default 10)")
    parser.add_argument("--depth", type=int, default=10, help="cells front-back (default 10)")
    parser.add_argument("--height", type=int, default=10,
                        help="cells up-down (default 10, use 1 for classic 2D)")
    parser.add_argument("--rocks", type=float, default=0.03,
                        help="share of cells filled with rocks, 0 to 0.2 (default 0.03)")
    parser.add_argument("--golden", type=float, default=0.3,
                        help="chance of a golden apple after each apple (default 0.3)")
    parser.add_argument("--speed", type=int, default=8, help="snake moves per second")
    parser.add_argument("--seed", type=int, default=None, help="random seed for repeatable games")
    parser.add_argument("--headless", action="store_true",
                        help="play without a window and print the results")
    parser.add_argument("--games", type=int, default=5,
                        help="number of games to play in headless mode")
    args = parser.parse_args()
    if not 0 <= args.rocks <= 0.2:
        parser.error("--rocks must be between 0 and 0.2")
    if not 0 <= args.golden <= 1:
        parser.error("--golden must be between 0 and 1")
    if args.width < 4 or args.depth < 4 or args.height < 1:
        parser.error("the world must be at least 4 x 4 x 1")
    return args


def run_headless(config: GameConfig, games: int, seed: int | None) -> None:
    """Let the AI play several games quickly and print the scores."""
    scores = []
    for number in range(1, games + 1):
        game_seed = None if seed is None else seed + number
        game = SnakeGame(config.width, config.depth, config.height,
                         config.rock_ratio, config.golden_chance, game_seed)
        agent = BFSAgent(game.board)
        max_steps = game.board.total_cells * 100  # safety limit against endless loops

        while not game.is_over and game.steps < max_steps:
            game.step(agent.choose_direction(game.snake, game.foods))

        scores.append(game.score)
        print(f"Game {number}: score={game.score} length={len(game.snake)} "
              f"golden={game.golden_eaten} steps={game.steps} result={game.status.name}")

    print(f"\nAverage score: {sum(scores) / len(scores):.1f}   Best score: {max(scores)}")


def main() -> None:
    args = parse_args()
    config = GameConfig(width=args.width, depth=args.depth, height=args.height,
                        rock_ratio=args.rocks, golden_chance=args.golden,
                        moves_per_second=max(1, args.speed))

    if args.headless:
        run_headless(config, max(1, args.games), args.seed)
    else:
        from snake_ai.app import SnakeApp  # imported here so headless mode needs no display
        SnakeApp(config, args.seed).run()


if __name__ == "__main__":
    main()
