"""Custom GitHub contribution snake animation with moving dots and projectiles."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image, ImageDraw


GRID_COLS = 53
GRID_ROWS = 7
CELL = 18
MARGIN = 24
FRAME_COUNT = 240
FRAME_RATE = 15
DOT_COUNT = 6
DOT_SPEED = 0.35
PROJECTILE_SPEED = 0.65
SNAKE_BASE_LENGTH = 6

BG_COLOR = (13, 17, 23)
GRID_COLOR = (26, 32, 44)
GRID_HIGHLIGHT = (37, 47, 63)
SNAKE_HEAD_COLOR = (125, 255, 160)
SNAKE_BODY_COLOR = (70, 192, 118)
PROJECTILE_COLOR = (255, 189, 68)
DOT_COLORS = [
    (244, 114, 182),
    (129, 140, 248),
    (96, 165, 250),
    (52, 211, 153),
    (248, 180, 83),
]


def wrap(value: float, limit: int) -> float:
    if value < 0:
        return value + limit
    if value >= limit:
        return value - limit
    return value


@dataclass
class Dot:
    x: float
    y: float
    color: Tuple[int, int, int]
    dx: float
    dy: float
    cooldown: int = field(default_factory=lambda: random.randint(15, 40))

    def step(self) -> None:
        self.x = wrap(self.x + self.dx, GRID_COLS)
        self.y = wrap(self.y + self.dy, GRID_ROWS)
        if random.random() < 0.15:
            self.dx = random.choice([-DOT_SPEED, 0.0, DOT_SPEED])
            self.dy = random.choice([-DOT_SPEED, 0.0, DOT_SPEED])
            if self.dx == 0 and self.dy == 0:
                self.dx = DOT_SPEED
        self.cooldown -= 1

    def ready_to_fire(self) -> bool:
        return self.cooldown <= 0

    def reset_cooldown(self) -> None:
        self.cooldown = random.randint(18, 48)


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    ttl: int = 40

    def step(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.ttl -= 1
        if self.ttl <= 0:
            return False
        if self.x < -2 or self.x > GRID_COLS + 2 or self.y < -2 or self.y > GRID_ROWS + 2:
            return False
        return True


@dataclass
class Snake:
    segments: List[Tuple[int, int]]
    desired_length: int = SNAKE_BASE_LENGTH

    def head(self) -> Tuple[int, int]:
        return self.segments[0]

    def grow(self, amount: int = 1) -> None:
        self.desired_length = min(self.desired_length + amount, 18)

    def move_toward(self, target: Tuple[int, int]) -> None:
        hx, hy = self.head()
        tx, ty = target

        dx = 0
        dy = 0
        if hx != tx:
            dx = 1 if (tx - hx) % GRID_COLS < (hx - tx) % GRID_COLS else -1
            if abs(tx - hx) <= GRID_COLS // 2:
                dx = 1 if tx > hx else -1
        elif hy != ty:
            dy = 1 if (ty - hy) % GRID_ROWS < (hy - ty) % GRID_ROWS else -1
            if abs(ty - hy) <= GRID_ROWS // 2:
                dy = 1 if ty > hy else -1
        else:
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

        if dx != 0 and dy != 0:
            if random.random() < 0.5:
                dy = 0
            else:
                dx = 0

        nx = (hx + dx) % GRID_COLS
        ny = (hy + dy) % GRID_ROWS
        self.segments.insert(0, (nx, ny))
        while len(self.segments) > self.desired_length:
            self.segments.pop()

    def hit(self, x: float, y: float) -> bool:
        for sx, sy in self.segments:
            if abs(sx + 0.5 - x) < 0.35 and abs(sy + 0.5 - y) < 0.35:
                return True
        return False


class Game:
    def __init__(self, seed: int = 1234) -> None:
        random.seed(seed)
        self.snake = Snake(segments=[(GRID_COLS // 2 - i, GRID_ROWS // 2) for i in range(SNAKE_BASE_LENGTH)])
        self.dots: List[Dot] = [self._spawn_dot() for _ in range(DOT_COUNT)]
        self.projectiles: List[Projectile] = []
        self.score = 0
        self.frame_logs: List[str] = []
        self.frame_index = 0

    def _spawn_dot(self) -> Dot:
        x = random.randint(0, GRID_COLS - 1) + 0.5
        y = random.randint(0, GRID_ROWS - 1) + 0.5
        color = random.choice(DOT_COLORS)
        dx = random.choice([-DOT_SPEED, 0.0, DOT_SPEED])
        dy = random.choice([-DOT_SPEED, 0.0, DOT_SPEED])
        if dx == 0 and dy == 0:
            dx = DOT_SPEED
        return Dot(x=x, y=y, color=color, dx=dx, dy=dy)

    def _nearest_dot(self) -> Tuple[int, int]:
        hx, hy = self.snake.head()
        best = None
        best_dist = float("inf")
        for dot in self.dots:
            dist = (dot.x - (hx + 0.5)) ** 2 + (dot.y - (hy + 0.5)) ** 2
            if dist < best_dist:
                best_dist = dist
                best = (int(dot.x), int(dot.y))
        if best is None:
            return hx, hy
        return best

    def update(self) -> None:
        target = self._nearest_dot()
        self.snake.move_toward(target)

        eaten = []
        for dot in self.dots:
            dot.step()
            if dot.ready_to_fire():
                proj = self._fire_projectile(dot)
                if proj:
                    self.projectiles.append(proj)
                    self._log(f"dot_fire ({dot.x:.2f},{dot.y:.2f}) → ({proj.vx:.2f},{proj.vy:.2f})")
                dot.reset_cooldown()
            hx, hy = self.snake.head()
            if int(dot.x) == hx and int(dot.y) == hy:
                eaten.append(dot)

        for dot in eaten:
            self.dots.remove(dot)
            self.snake.grow()
            self.score += 1
            self._log(f"dot_eaten ({dot.x:.1f},{dot.y:.1f}) score={self.score}")
            self.dots.append(self._spawn_dot())

        survivors: List[Projectile] = []
        for proj in self.projectiles:
            if proj.step():
                if self.snake.hit(proj.x, proj.y):
                    self._log(f"snake_hit ({proj.x:.2f},{proj.y:.2f})")
                    continue
                survivors.append(proj)
        self.projectiles = survivors
        self.frame_index += 1

    def _fire_projectile(self, dot: Dot) -> Projectile | None:
        hx, hy = self.snake.head()
        sx = hx + 0.5
        sy = hy + 0.5
        dx = sx - dot.x
        dy = sy - dot.y
        dist = math.hypot(dx, dy)
        if dist < 1e-5:
            return None
        vx = (dx / dist) * PROJECTILE_SPEED
        vy = (dy / dist) * PROJECTILE_SPEED
        return Projectile(x=dot.x, y=dot.y, vx=vx, vy=vy)

    def _log(self, message: str) -> None:
        self.frame_logs.append(f"[{self.frame_index:03d}] {message}")


def draw_frame(game: Game) -> Image.Image:
    width = MARGIN * 2 + GRID_COLS * CELL
    height = MARGIN * 2 + GRID_ROWS * CELL
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    for col in range(GRID_COLS):
        for row in range(GRID_ROWS):
            x0 = MARGIN + col * CELL
            y0 = MARGIN + row * CELL
            color = GRID_HIGHLIGHT if (col + row) % 2 else GRID_COLOR
            draw.rounded_rectangle([x0, y0, x0 + CELL - 2, y0 + CELL - 2], radius=4, fill=color)

    for proj in game.projectiles:
        cx = MARGIN + proj.x * CELL
        cy = MARGIN + proj.y * CELL
        r = CELL * 0.18
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PROJECTILE_COLOR)

    for dot in game.dots:
        cx = MARGIN + dot.x * CELL
        cy = MARGIN + dot.y * CELL
        r = CELL * 0.38
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dot.color)
        draw.ellipse([cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6], fill=tuple(min(255, c + 25) for c in dot.color))

    for idx, (sx, sy) in enumerate(game.snake.segments):
        cx = MARGIN + (sx + 0.5) * CELL
        cy = MARGIN + (sy + 0.5) * CELL
        r = CELL * (0.45 if idx == 0 else 0.42)
        color = SNAKE_HEAD_COLOR if idx == 0 else SNAKE_BODY_COLOR
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    info = f"Score {game.score}"
    draw.text((MARGIN, height - MARGIN // 2), info, fill=(180, 198, 255))
    return img


def generate_animation(frames: Iterable[Image.Image], output: Path) -> None:
    frames = list(frames)
    if not frames:
        raise RuntimeError("No frames generated")
    first, *rest = frames
    duration_ms = int(1000 / FRAME_RATE)
    first.save(output, save_all=True, append_images=rest, format="GIF", optimize=False, duration=duration_ms, loop=0)


def main() -> None:
    dist_dir = Path("dist")
    dist_dir.mkdir(parents=True, exist_ok=True)
    gif_path = dist_dir / "custom_snake.gif"
    log_path = dist_dir / "custom_snake_log.txt"

    game = Game()
    frames: List[Image.Image] = []
    for _ in range(FRAME_COUNT):
        frames.append(draw_frame(game))
        game.update()

    generate_animation(frames, gif_path)
    log_path.write_text("\n".join(game.frame_logs) or "No notable events", encoding="utf-8")
    print(f"Wrote {gif_path} with {len(frames)} frames (score {game.score})")


if __name__ == "__main__":
    main()
