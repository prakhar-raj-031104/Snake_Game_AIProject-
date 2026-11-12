"""Draws the game with Pygame. Only this file knows about graphics."""

import pygame

from .config import GameConfig
from .game import GameStatus, SnakeGame
from .geometry import Point


class Renderer:
    """Turns the game state into pixels on the screen."""

    def __init__(self, config: GameConfig, screen: pygame.Surface) -> None:
        self.config = config
        self.screen = screen
        try:
            self.font = pygame.font.SysFont("arial", 22, bold=True)
            self.big_font = pygame.font.SysFont("arial", 40, bold=True)
        except Exception:
            self.font = None
            self.big_font = None

    def draw(self, game: SnakeGame, path: list[Point], paused: bool,
             show_path: bool) -> None:
        self.screen.fill(self.config.background_color)
        self._draw_grid(game)
        if show_path:
            self._draw_path(path)
        self._draw_food(game)
        self._draw_snake(game)
        self._draw_hud(game, paused)
        if game.is_over:
            self._draw_end_message(game.status)
        pygame.display.flip()

    # ----- helpers -------------------------------------------------------

    def _cell_rect(self, point: Point, padding: int = 1) -> pygame.Rect:
        size = self.config.cell_size
        return pygame.Rect(
            point.x * size + padding,
            point.y * size + self.config.hud_height + padding,
            size - 2 * padding,
            size - 2 * padding,
        )

    def _draw_grid(self, game: SnakeGame) -> None:
        for cell in game.board.all_cells():
            pygame.draw.rect(self.screen, self.config.grid_color,
                             self._cell_rect(cell, padding=0), width=1)

    def _draw_path(self, path: list[Point]) -> None:
        for cell in path[:-1]:  # the last cell is the food itself
            pygame.draw.rect(self.screen, self.config.path_color,
                             self._cell_rect(cell, padding=8), border_radius=4)

    def _draw_food(self, game: SnakeGame) -> None:
        if game.food.position is not None:
            rect = self._cell_rect(game.food.position, padding=4)
            pygame.draw.ellipse(self.screen, self.config.food_color, rect)

    def _draw_snake(self, game: SnakeGame) -> None:
        for index, cell in enumerate(game.snake.body):
            color = (self.config.snake_head_color if index == 0
                     else self.config.snake_body_color)
            pygame.draw.rect(self.screen, color, self._cell_rect(cell, padding=2),
                             border_radius=6)

    def _draw_hud(self, game: SnakeGame, paused: bool) -> None:
        if self.font is None:
            return
        text = f"Score: {game.score}    Length: {len(game.snake)}    Steps: {game.steps}"
        if paused:
            text += "    [PAUSED]"
        surface = self.font.render(text, True, self.config.text_color)
        self.screen.blit(surface, (10, (self.config.hud_height - surface.get_height()) // 2))

    def _draw_end_message(self, status: GameStatus) -> None:
        if self.font is None or self.big_font is None:
            return
        message = "YOU WIN!" if status == GameStatus.WON else "GAME OVER"
        lines = [(message, self.big_font), ("Press R to restart, ESC to quit", self.font)]

        width, height = self.config.window_size
        y = height // 2 - 40
        for text, font in lines:
            surface = font.render(text, True, self.config.text_color)
            self.screen.blit(surface, ((width - surface.get_width()) // 2, y))
            y += surface.get_height() + 10
