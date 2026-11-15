"""All tunable settings live here, so nothing is hard-coded elsewhere."""

from dataclasses import dataclass

Color = tuple[int, int, int]


@dataclass(frozen=True)
class GameConfig:
    """Settings for the world, speed, window and colours."""

    # World size (height 1 = classic flat Snake)
    width: int = 10
    depth: int = 10
    height: int = 10
    rock_ratio: float = 0.03      # share of cells filled with rocks
    golden_chance: float = 0.3    # chance a golden apple appears after an apple

    # Speed and window
    moves_per_second: int = 8
    window_width: int = 1100
    window_height: int = 800
    hud_height: int = 56

    # Colours
    background_color: Color = (14, 19, 32)
    floor_color: Color = (24, 32, 52)
    grid_color: Color = (44, 56, 84)
    box_color: Color = (60, 74, 108)
    shadow_color: Color = (10, 14, 24)
    snake_head_color: Color = (184, 255, 201)
    snake_body_color: Color = (63, 191, 106)
    snake_tail_color: Color = (30, 110, 70)
    rock_color: Color = (120, 112, 128)
    apple_color: Color = (255, 92, 70)
    golden_color: Color = (255, 205, 60)
    path_color: Color = (122, 162, 255)
    text_color: Color = (240, 240, 240)
    muted_text_color: Color = (150, 160, 185)
