"""Connects everything: the game rules, the AI agent and the Pygame window."""

import pygame

from .agent import BFSAgent
from .config import GameConfig
from .game import SnakeGame
from .renderer import Renderer

MIN_FPS, MAX_FPS = 1, 120


class SnakeApp:
    """Runs the main loop: handle input -> AI picks a move -> update -> draw."""

    def __init__(self, config: GameConfig, seed: int | None = None) -> None:
        self.config = config
        self.game = SnakeGame(config.grid_width, config.grid_height, seed)
        self.agent = BFSAgent(self.game.board)
        self.fps = config.fps
        self.paused = False
        self.show_path = True
        self.running = True

    def run(self) -> None:
        pygame.display.init()  # only what we need (no audio)
        pygame.font.init()
        try:
            screen = pygame.display.set_mode(self.config.window_size)
            pygame.display.set_caption("Snake AI - Breadth-First Search")
            renderer = Renderer(self.config, screen)
            clock = pygame.time.Clock()

            while self.running:
                self._handle_events()
                if not self.paused and not self.game.is_over:
                    direction = self.agent.choose_direction(
                        self.game.snake, self.game.food.position)
                    self.game.step(direction)
                renderer.draw(self.game, self.agent.current_path,
                              self.paused, self.show_path)
                clock.tick(self.fps)
        finally:
            pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key: int) -> None:
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_r:
            self.game.reset()
            self.agent.current_path = []
        elif key == pygame.K_p:
            self.show_path = not self.show_path
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS, pygame.K_UP):
            self.fps = min(MAX_FPS, self.fps + 5)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_DOWN):
            self.fps = max(MIN_FPS, self.fps - 5)
