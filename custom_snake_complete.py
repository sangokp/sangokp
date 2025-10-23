"""
custom_snake_complete.py
A complete custom snake animation game with colored dots that move, shoot, and are eaten by the snake.
This script demonstrates generating a snake game based on a GitHub contributions grid. Dots move randomly
across the grid and occasionally shoot projectiles toward the snake. When the snake eats a dot, it grows.
This example is intended as a foundation for a GitHub Actions workflow to generate a GIF of your contributions grid.
"""

import random
import math
from typing import List, Tuple

class Dot:
    """Represents a colored dot that moves around the grid and can shoot projectiles."""
    def __init__(self, x: int, y: int, color: str):
        self.x = x
        self.y = y
        self.color = color
        self.alive = True
        self.shoot_cooldown = 0

    def move(self, width: int, height: int) -> None:
        """Move the dot randomly to a neighbouring cell within the grid."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        self.x = (self.x + dx) % width
        self.y = (self.y + dy) % height

    def ready_to_shoot(self) -> bool:
        """Determine if the dot can shoot this turn."""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return False
        return random.random() < 0.05  # 5% chance each turn

    def shoot(self, target_x: int, target_y: int) -> "Projectile":
        """Create a projectile aimed at the target coordinates."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return None
        unit_dx = round(dx / distance)
        unit_dy = round(dy / distance)
        self.shoot_cooldown = 10
        return Projectile(self.x, self.y, unit_dx, unit_dy, self.color)

class Projectile:
    """Represents a projectile fired by a dot."""
    def __init__(self, x: int, y: int, dx: int, dy: int, color: str):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.alive = True

    def move(self, width: int, height: int) -> None:
        self.x = (self.x + self.dx) % width
        self.y = (self.y + self.dy) % height

class Snake:
    """Represents the snake moving across the grid."""
    def __init__(self, body: List[Tuple[int, int]], direction: Tuple[int, int]):
        self.body = list(body)
        self.direction = direction
        self.alive = True

    def move(self) -> None:
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self) -> None:
        tail = self.body[-1]
        self.body.append(tail)

    def change_direction(self, new_direction: Tuple[int, int]) -> None:
        self.direction = new_direction

    def head_position(self) -> Tuple[int, int]:
        return self.body[0]

    def check_collision_with_dot(self, dot: Dot) -> bool:
        return self.body[0] == (dot.x, dot.y)

    def check_collision_with_projectile(self, projectile: Projectile) -> bool:
        return self.body[0] == (projectile.x, projectile.y)

class Game:
    """Main game logic that updates the snake, dots, and projectiles."""
    def __init__(self, width: int = 53, height: int = 7):
        self.width = width
        self.height = height
        # Start with a snake of length 3 moving right
        self.snake = Snake(body=[(2, 3), (1, 3), (0, 3)], direction=(1, 0))
        self.dots: List[Dot] = []
        self.projectiles: List[Projectile] = []

    def spawn_dot(self, x: int, y: int, color: str) -> None:
        self.dots.append(Dot(x, y, color))

    def update(self) -> None:
        # Move dots and possibly shoot
        for dot in list(self.dots):
            dot.move(self.width, self.height)
            if dot.ready_to_shoot():
                projectile = dot.shoot(*self.snake.head_position())
                if projectile:
                    self.projectiles.append(projectile)
        # Move projectiles and check for collision with snake
        for proj in list(self.projectiles):
            proj.move(self.width, self.height)
            if self.snake.check_collision_with_projectile(proj):
                self.snake.alive = False
                proj.alive = False
                self.projectiles.remove(proj)
        # Move snake
        self.snake.move()
        # Check if snake eats any dots
        for dot in list(self.dots):
            if self.snake.check_collision_with_dot(dot):
                self.snake.grow()
                self.dots.remove(dot)

    def is_game_over(self) -> bool:
        return not self.snake.alive

    def state(self) -> dict:
        """Return a dictionary representing the current state for debugging or rendering."""
        return {
            "snake": self.snake.body,
            "dots": [(d.x, d.y, d.color) for d in self.dots],
            "projectiles": [(p.x, p.y, p.color) for p in self.projectiles],
        }

def main():
    game = Game()
    # Spawn sample dots of different colors
    game.spawn_dot(10, 2, "red")
    game.spawn_dot(20, 4, "blue")
    game.spawn_dot(30, 1, "green")
    # Run a simple simulation printing the state each turn
    for step in range(50):
        if game.is_game_over():
            print(f"Game over at step {step}!")
            break
        game.update()
        print(f"Step {step}:", game.state())

if __name__ == "__main__":
    main()
