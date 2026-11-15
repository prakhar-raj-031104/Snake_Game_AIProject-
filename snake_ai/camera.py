"""A simple 3D camera that orbits around the world and projects it onto the screen.

The maths is just two rotations and a perspective divide:
  1. Move the world so the centre of the board is at the origin.
  2. Turn it around the vertical axis (yaw) and tilt it (pitch).
  3. Divide by depth, so things further away look smaller.
"""

import math

Vector = tuple[float, float, float]

MIN_PITCH, MAX_PITCH = 0.15, 1.45   # radians: from almost side-on to almost top-down


class Camera:
    """Orbits around a target point. Call `update()` once per frame."""

    def __init__(self, target: Vector, distance: float, focal_length: float,
                 screen_center: tuple[float, float],
                 yaw: float = 0.6, pitch: float = 0.6) -> None:
        self.target = target
        self.distance = distance
        self.min_distance = distance * 0.5
        self.max_distance = distance * 2.0
        self.focal_length = focal_length
        self.screen_center = screen_center
        self.yaw = yaw
        self.pitch = pitch
        self.update()

    def orbit(self, delta_yaw: float, delta_pitch: float = 0.0) -> None:
        """Rotate around the target (drag with the mouse or use arrow keys)."""
        self.yaw = (self.yaw + delta_yaw) % math.tau
        self.pitch = min(MAX_PITCH, max(MIN_PITCH, self.pitch + delta_pitch))

    def zoom(self, factor: float) -> None:
        self.distance = min(self.max_distance,
                            max(self.min_distance, self.distance * factor))

    def update(self) -> None:
        """Cache sine/cosine values for this frame."""
        self._cos_yaw, self._sin_yaw = math.cos(self.yaw), math.sin(self.yaw)
        self._cos_pitch, self._sin_pitch = math.cos(self.pitch), math.sin(self.pitch)

    def rotate(self, x: float, y: float, z: float) -> Vector:
        """Turn a direction vector into camera space (right, up, depth)."""
        x1 = x * self._cos_yaw - y * self._sin_yaw
        y1 = x * self._sin_yaw + y * self._cos_yaw
        up = y1 * self._sin_pitch + z * self._cos_pitch
        depth = y1 * self._cos_pitch - z * self._sin_pitch
        return x1, up, depth

    def to_view(self, x: float, y: float, z: float) -> Vector:
        """World position -> camera space position."""
        tx, ty, tz = self.target
        right, up, depth = self.rotate(x - tx, y - ty, z - tz)
        return right, up, depth + self.distance

    def to_screen(self, view: Vector) -> tuple[float, float]:
        """Camera space position -> pixel position (perspective projection)."""
        right, up, depth = view
        depth = max(depth, 0.1)
        cx, cy = self.screen_center
        return (cx + self.focal_length * right / depth,
                cy - self.focal_length * up / depth)

    def project(self, x: float, y: float, z: float) -> tuple[float, float]:
        return self.to_screen(self.to_view(x, y, z))

    def scale_at(self, depth: float) -> float:
        """How many pixels one world unit covers at this depth."""
        return self.focal_length / max(depth, 0.1)
