"""All tunable settings live here, so nothing is hard-coded elsewhere."""

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class GameConfig:
    """Settings for the board, speed and colours."""

    grid_width: int = 20          # number of columns
    grid_height: int = 20         # number of rows
    cell_size: int = 30           # size of one cell in pixels
    fps: int = 15                 # game speed (moves per second)
    hud_height: int = 40          # height of the score bar on top

    background_color: Color = (20, 20, 30)
    grid_color: Color = (35, 35, 50)
    snake_head_color: Color = (80, 220, 100)
    snake_body_color: Color = (40, 160, 70)
    food_color: Color = (230, 70, 70)
    path_color: Color = (70, 90, 170)
    text_color: Color = (240, 240, 240)

    @property
    def window_size(self) -> tuple[int, int]:
        """Pixel size of the whole window (board + score bar)."""
        width = self.grid_width * self.cell_size
        height = self.grid_height * self.cell_size + self.hud_height
        return width, height
