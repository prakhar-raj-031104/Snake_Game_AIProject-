"""Connects everything: the game rules, the AI agent and the Pygame window."""

import pygame

from .agent import BFSAgent
from .config import GameConfig
from .game import SnakeGame
from .renderer import Renderer

RENDER_FPS = 60              # the picture updates smoothly...
MIN_SPEED, MAX_SPEED = 1, 60  # ...while the snake moves this many times per second
AUTO_ROTATE_SPEED = 0.15      # radians per second
KEY_ROTATE_STEP = 0.08
DRAG_SENSITIVITY = 0.008


class SnakeApp:
    """Runs the main loop: handle input -> AI picks a move -> update -> draw."""

    def __init__(self, config: GameConfig, seed: int | None = None) -> None:
        self.config = config
        self.game = SnakeGame(config.width, config.depth, config.height,
                              config.rock_ratio, config.golden_chance, seed)
        self.agent = BFSAgent(self.game.board)
        self.speed = config.moves_per_second
        self.paused = False
        self.show_path = True
        self.auto_rotate = True
        self.dragging = False
        self.running = True

    def run(self) -> None:
        pygame.display.init()  # only what we need (no audio)
        try:
            pygame.font.init()
        except Exception:
            pass  # the game still runs without text
        try:
            screen = pygame.display.set_mode((self.config.window_width, self.config.window_height))
            pygame.display.set_caption("Snake AI 3D - Breadth-First Search")
            self.renderer = Renderer(self.config, screen, self.game)
            clock = pygame.time.Clock()
            time_since_move = 0.0

            while self.running:
                dt = clock.tick(RENDER_FPS) / 1000
                self._handle_events()

                time_since_move += dt
                if time_since_move >= 1 / self.speed:
                    time_since_move = 0.0
                    if not self.paused and not self.game.is_over:
                        direction = self.agent.choose_direction(self.game.snake, self.game.foods)
                        self.game.step(direction)

                if self.auto_rotate and not self.dragging:
                    self.renderer.camera.orbit(AUTO_ROTATE_SPEED * dt)
                self.renderer.draw(self.game, self.agent.current_path, self.paused,
                                   self.show_path, self.speed, dt)
        finally:
            pygame.quit()

    # ----- input -------------------------------------------------------------

    def _handle_events(self) -> None:
        camera = self.renderer.camera
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx, dy = event.rel
                camera.orbit(-dx * DRAG_SENSITIVITY, dy * DRAG_SENSITIVITY)
            elif event.type == pygame.MOUSEWHEEL:
                camera.zoom(0.9 if event.y > 0 else 1.1)

    def _handle_key(self, key: int) -> None:
        camera = self.renderer.camera
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.running = False
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        elif key == pygame.K_r:
            self.game.reset()
            self.agent.current_path = []
        elif key == pygame.K_p:
            self.show_path = not self.show_path
        elif key == pygame.K_a:
            self.auto_rotate = not self.auto_rotate
        elif key == pygame.K_LEFT:
            camera.orbit(KEY_ROTATE_STEP)
        elif key == pygame.K_RIGHT:
            camera.orbit(-KEY_ROTATE_STEP)
        elif key == pygame.K_UP:
            camera.orbit(0, KEY_ROTATE_STEP)
        elif key == pygame.K_DOWN:
            camera.orbit(0, -KEY_ROTATE_STEP)
        elif key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.speed = min(MAX_SPEED, self.speed + 2)
        elif key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.speed = max(MIN_SPEED, self.speed - 2)
