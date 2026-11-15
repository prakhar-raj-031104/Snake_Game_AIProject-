"""Draws the 3D world with Pygame. Only this file knows about graphics.

Pygame only draws flat shapes, so we build the 3D look ourselves:
  * every cube is projected with the Camera and drawn face by face,
  * faces pointing away from the camera are skipped (back-face culling),
  * objects are drawn from far to near (the "painter's algorithm"),
  * each face is shaded by how much it faces the light.
"""

import math

import pygame

from .camera import Camera
from .config import Color, GameConfig
from .food import GOLDEN, Food
from .game import GameStatus, SnakeGame
from .geometry import Point

# The 8 corners of a cube (as -1/+1 offsets) and its 6 faces:
# (corner indices in drawing order, outward normal).
CORNERS = [(1 if i & 1 else -1, 1 if i & 2 else -1, 1 if i & 4 else -1) for i in range(8)]
FACES = [
    ((1, 3, 7, 5), (1, 0, 0)), ((0, 4, 6, 2), (-1, 0, 0)),
    ((2, 6, 7, 3), (0, 1, 0)), ((0, 1, 5, 4), (0, -1, 0)),
    ((4, 5, 7, 6), (0, 0, 1)), ((0, 2, 3, 1), (0, 0, -1)),
]
_LIGHT = (-0.35, -0.55, 0.76)  # roughly "from above, front left"
FACE_SHADES = [0.45 + 0.55 * max(0.0, sum(n * l for n, l in zip(normal, _LIGHT)))
               for _, normal in FACES]


def shade(color: Color, amount: float) -> Color:
    return tuple(max(0, min(255, int(c * amount))) for c in color)  # type: ignore[return-value]


def blend(a: Color, b: Color, t: float) -> Color:
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))  # type: ignore[return-value]


def load_font(size: int, bold: bool = False) -> pygame.font.Font | None:
    """Load a font, or return None if fonts are unavailable (game still runs)."""
    try:
        return pygame.font.SysFont("arial", size, bold=bold)
    except Exception:
        try:
            return pygame.font.Font(None, size + 6)
        except Exception:
            return None


class Renderer:
    """Turns the game state into pixels on the screen."""

    def __init__(self, config: GameConfig, screen: pygame.Surface, game: SnakeGame) -> None:
        self.config = config
        self.screen = screen
        self.font = load_font(20, bold=True)
        self.small_font = load_font(16)
        self.big_font = load_font(44, bold=True)
        self.camera = self._make_camera(game)
        self.time = 0.0

    def _make_camera(self, game: SnakeGame) -> Camera:
        board = game.board
        width, height = self.screen.get_size()
        view_height = height - self.config.hud_height
        size = max(board.width, board.depth, board.height)
        radius = 0.5 * math.sqrt(board.width ** 2 + board.depth ** 2 + board.height ** 2)
        distance = size * 2.4
        focal = 0.42 * min(width, view_height) * distance / radius
        center = (width / 2, self.config.hud_height + view_height / 2)
        target = ((board.width - 1) / 2, (board.depth - 1) / 2, (board.height - 1) / 2)
        return Camera(target, distance, focal, center)

    # ----- main entry point ------------------------------------------------

    def draw(self, game: SnakeGame, path: list[Point], paused: bool,
             show_path: bool, speed: int, dt: float) -> None:
        self.time += dt
        self.camera.update()
        self._precompute_rotations()

        self.screen.fill(self.config.background_color)
        self._draw_floor(game)
        self._draw_shadows(game)

        # Collect everything, then draw from far to near.
        items: list[tuple[float, callable]] = []
        body = game.snake.body
        for index, cell in enumerate(body):
            items.append(self._cube(cell, 0.43, self._snake_color(index, len(body))))
        for rock in game.board.rocks:
            items.append(self._cube(rock, 0.47, self.config.rock_color))
        for food in game.foods:
            items.append(self._food(food))
        if show_path:
            for cell in path[:-1]:
                items.append(self._dot(cell))

        items.sort(key=lambda item: item[0], reverse=True)
        for _, draw in items:
            draw()
        self._draw_food_markers(game)

        self._draw_hud(game, paused, show_path, speed)
        if game.is_over:
            self._draw_end_message(game.status)
        pygame.display.flip()

    # ----- 3D objects ------------------------------------------------------

    def _precompute_rotations(self) -> None:
        self._corner_offsets = [self.camera.rotate(*corner) for corner in CORNERS]
        self._face_normals = [self.camera.rotate(*normal) for _, normal in FACES]

    def _cube(self, cell: Point, half: float, color: Color):
        center = self.camera.to_view(*cell)

        def draw() -> None:
            cx, cy, cz = center
            corners = [self.camera.to_screen((cx + ox * half, cy + oy * half, cz + oz * half))
                       for ox, oy, oz in self._corner_offsets]
            for (indices, _), normal, light in zip(FACES, self._face_normals, FACE_SHADES):
                nx, ny, nz = normal
                # Back-face culling: skip faces pointing away from the camera.
                if (cx + nx * half) * nx + (cy + ny * half) * ny + (cz + nz * half) * nz >= 0:
                    continue
                polygon = [corners[i] for i in indices]
                pygame.draw.polygon(self.screen, shade(color, light), polygon)
                pygame.draw.polygon(self.screen, shade(color, light * 0.7), polygon, 1)

        return center[2], draw

    def _food(self, food: Food):
        center = self.camera.to_view(*food.position)
        is_golden = food.kind is GOLDEN
        color = self.config.golden_color if is_golden else self.config.apple_color

        def draw() -> None:
            x, y = self.camera.to_screen(center)
            scale = self.camera.scale_at(center[2])
            radius = 0.34 * scale
            if is_golden:  # golden apples pulse so they catch the eye
                radius *= 1 + 0.12 * math.sin(self.time * 8)
                pygame.draw.circle(self.screen, shade(color, 0.45), (x, y), radius * 1.45, 2)
            floor = self.camera.project(food.position.x, food.position.y, -0.5)
            pygame.draw.line(self.screen, shade(color, 0.45), (x, y), floor, 1)
            pygame.draw.circle(self.screen, color, (x, y), radius)
            pygame.draw.circle(self.screen, blend(color, (255, 255, 255), 0.6),
                               (x - radius * 0.3, y - radius * 0.3), radius * 0.3)

        return center[2], draw

    def _draw_food_markers(self, game: SnakeGame) -> None:
        """Outline rings drawn last, so food stays visible even behind the snake."""
        for food in game.foods:
            view = self.camera.to_view(*food.position)
            color = self.config.golden_color if food.kind is GOLDEN else self.config.apple_color
            radius = 0.5 * self.camera.scale_at(view[2])
            pygame.draw.circle(self.screen, color, self.camera.to_screen(view), radius, 2)

    def _dot(self, cell: Point):
        center = self.camera.to_view(*cell)

        def draw() -> None:
            radius = max(2.0, 0.1 * self.camera.scale_at(center[2]))
            pygame.draw.circle(self.screen, self.config.path_color,
                               self.camera.to_screen(center), radius)

        return center[2], draw

    def _snake_color(self, index: int, length: int) -> Color:
        if index == 0:
            return self.config.snake_head_color
        return blend(self.config.snake_body_color, self.config.snake_tail_color,
                     index / max(1, length - 1))

    # ----- floor, box and shadows ------------------------------------------

    def _draw_floor(self, game: SnakeGame) -> None:
        board, project = game.board, self.camera.project
        x0, y0, x1, y1, z = -0.5, -0.5, board.width - 0.5, board.depth - 0.5, -0.5
        floor = [project(x0, y0, z), project(x1, y0, z), project(x1, y1, z), project(x0, y1, z)]
        pygame.draw.polygon(self.screen, self.config.floor_color, floor)
        for i in range(board.width + 1):
            pygame.draw.line(self.screen, self.config.grid_color,
                             project(i - 0.5, y0, z), project(i - 0.5, y1, z), 1)
        for j in range(board.depth + 1):
            pygame.draw.line(self.screen, self.config.grid_color,
                             project(x0, j - 0.5, z), project(x1, j - 0.5, z), 1)

        # The edges of the world's bounding box.
        top = board.height - 0.5
        corners = [(x, y, zz) for zz in (z, top) for y in (y0, y1) for x in (x0, x1)]
        edges = [(0, 1), (2, 3), (0, 2), (1, 3), (4, 5), (6, 7), (4, 6), (5, 7),
                 (0, 4), (1, 5), (2, 6), (3, 7)]
        for a, b in edges:
            pygame.draw.line(self.screen, self.config.box_color,
                             project(*corners[a]), project(*corners[b]), 1)

    def _draw_shadows(self, game: SnakeGame) -> None:
        """Dark spots on the floor help you see where things are in 3D."""
        cells = [game.snake.head] + [food.position for food in game.foods]
        squash = math.sin(self.camera.pitch)
        for cell in cells:
            view = self.camera.to_view(cell.x, cell.y, -0.5)
            x, y = self.camera.to_screen(view)
            radius = 0.35 * self.camera.scale_at(view[2])
            rect = pygame.Rect(0, 0, radius * 2, max(2, radius * 2 * squash))
            rect.center = (int(x), int(y))
            pygame.draw.ellipse(self.screen, self.config.shadow_color, rect)

    # ----- text --------------------------------------------------------------

    def _text(self, font, text: str, color: Color, pos: tuple[float, float],
              center: bool = False) -> None:
        if font is None:
            return
        surface = font.render(text, True, color)
        x, y = pos
        if center:
            x -= surface.get_width() / 2
        self.screen.blit(surface, (x, y))

    def _draw_hud(self, game: SnakeGame, paused: bool, show_path: bool, speed: int) -> None:
        width, height = self.screen.get_size()
        pygame.draw.rect(self.screen, (20, 27, 44), (0, 0, width, self.config.hud_height))

        stats = (f"Score {game.score}     Length {len(game.snake)}     "
                 f"Golden {game.golden_eaten}     Steps {game.steps}     Speed {speed}")
        if paused:
            stats += "     [PAUSED]"
        self._text(self.font, stats, self.config.text_color, (16, 16))

        golden = game.golden_apple
        if golden is not None:
            self._text(self.font, f"GOLDEN APPLE: {golden.moves_left} moves left!",
                       self.config.golden_color, (width - 330, 16))

        hint = ("Drag: rotate   Scroll: zoom   Space: pause   R: restart   "
                f"P: path {'on' if show_path else 'off'}   A: auto-rotate   +/-: speed   Esc: quit")
        self._text(self.small_font, hint, self.config.muted_text_color, (width / 2, height - 28),
                   center=True)

    def _draw_end_message(self, status: GameStatus) -> None:
        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        message = "YOU WIN!" if status == GameStatus.WON else "GAME OVER"
        self._text(self.big_font, message, self.config.text_color,
                   (width / 2, height / 2 - 50), center=True)
        self._text(self.font, "Press R to restart, Esc to quit", self.config.text_color,
                   (width / 2, height / 2 + 10), center=True)
