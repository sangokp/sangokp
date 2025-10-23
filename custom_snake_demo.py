"""
custom_snake_demo.py
A custom snake animation with colored dots that move and shoot.
This script demonstrates a skeleton for generating a snake game animation from a GitHub contributions grid.
Dots move randomly and occasionally shoot projectiles at the snake. When the snake eats a dot, it grows.
"""

import random
import math

class Dot:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.alive = True
        self.shoot_cooldown = 0

    def move(self, width, height):
        """Move the dot randomly to a neighbouring cell within the grid."""
        # Choose a random direction from the 4-neighbourhood
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dx, dy = random.choice(directions)
        new_x = (self.x + dx) % width
        new_y = (self.y + dy) % height
        self.x, self.y = new_x, new_y

    def ready_to_shoot(self):
        """Return True if the dot can shoot this turn."""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            return False
        # random chance to shoot
        return random.random() < 0.1

    def shoot(self, target_x, target_y):
        """Create a projectile that moves toward the target coordinates."""
        # Compute direction vector from the dot to the target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return None
        # Normalize to step of 1 cell per update
        unit_dx = round(dx / distance)
        unit_dy = round(dy / distance)
        self.shoot_cooldown = 5
        return Projectile(self.x, self.y, unit_dx, unit_dy, self.color)

class Projectile:
    def __init__(self, x, y, dx, dy, color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.alive = True

    def move(self, width, height):
        """Move the projectile one step in its direction."""
        self.x = (self.x + self.dx) % width
        self.y = (self.y + self.dy) % height

class Snake:
    def __init__(self, body, direction):
        self.body = list(body)
        self.direction = direction  # (dx, dy)
        self.alive = True

    def move(self):
        """Move the snake forward by one cell."""
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        # Insert new head and remove tail
        self.body.insert(0, new_head)
        self.body.pop()

    def grow(self):
        """Grow the snake by adding an extra segment at the tail."""
        tail = self.body[-1]
        self.body.append(tail)

    def check_collision_with_dot(self, dot):
        return self.body[0] == (dot.x, dot.y)

    def check_collision_with_projectile(self, projectile):
        return self.body[0] == (projectile.x, projectile.y)

class Game:
    def __init__(self, width=53, height=7):
        self.width = width
        self.height = height
        self.snake = Snake(body=[(0, 0), (-1, 0), (-2, 0)], direction=(1, 0))
        self.dots = []
        self.projectiles = []

    def spawn_dot(self, x, y, color):
        self.dots.append(Dot(x, y, color))

    def update(self):
        # Move dots and maybe shoot
        for dot in list(self.dots):
            dot.move(self.width, self.height)
            if dot.ready_to_shoot():
                projectile = dot.shoot(self.snake.body[0][0], self.snake.body[0][1])
                if projectile:
                    self.projectiles.append(projectile)

        # Move projectiles
        for proj in list(self.projectiles):
            proj.move(self.width, self.height)
            if self.snake.check_collision_with_projectile(proj):
                # For demo purposes, mark snake as not alive
                self.snake.alive = False
                proj.alive = False
                self.projectiles.remove(proj)

        # Move snake
        self.snake.move()

        # Check snake eating dots
        for dot in list(self.dots):
            if self.snake.check_collision_with_dot(dot):
                self.snake.grow()
                self.dots.remove(dot)

def main():
    game = Game()
    # Spawn some colored dots
    game.spawn_dot(10, 3, "red")
    game.spawn_dot(20, 5, "blue")
    game.spawn_dot(30, 2, "green")
    # Simulate update loops
    for _ in range(20):
        game.update()
        # For demonstration we print some state
        print("Snake head:", game.snake.body[0], "Dots:", [(d.x, d.y) for d in game.dots], "Projectiles:", [(p.x, p.y) for p in game.projectiles])

if __name__ == "__main__":
    main()
