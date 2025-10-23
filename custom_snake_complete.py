"""
custom_snake_complete.py
A complete custom snake animation game with colored dots that move, shoot, and are eaten by the snake.
This script demonstrates generating a snake game based on a GitHub contributions grid. Dots move randomly
across the grid and occasionally shoot projectiles toward the snake. When the snake eats a dot, it grows.
This example is intended as a foundation for a GitHub Actions workflow to generate a GIF of your contributions grid.
"""

import random
import math
import os
from typing import List, Tuple
from PIL import Image, ImageDraw

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
        # Start with a snake of length 6 moving right
        self.snake = Snake(body=[(5, 3), (4, 3), (3, 3), (2, 3), (1, 3), (0, 3)], direction=(1, 0))
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

def render_frame(game: Game, cell_size: int = 15) -> Image.Image:
    """Render the current game state as a PIL Image."""
    width = game.width * cell_size
    height = game.height * cell_size
    
    # Create image with dark background
    img = Image.new('RGB', (width, height), color='#0D1117')
    draw = ImageDraw.Draw(img)
    
    # Draw grid lines
    for i in range(game.width + 1):
        x = i * cell_size
        draw.line([(x, 0), (x, height)], fill='#21262D', width=1)
    for i in range(game.height + 1):
        y = i * cell_size
        draw.line([(0, y), (width, y)], fill='#21262D', width=1)
    
    # Draw dots
    for dot_x, dot_y, color in game.state()['dots']:
        x = dot_x * cell_size
        y = dot_y * cell_size
        draw.rectangle(
            [x + 2, y + 2, x + cell_size - 2, y + cell_size - 2],
            fill=color
        )
    
    # Draw projectiles
    for proj_x, proj_y, color in game.state()['projectiles']:
        x = proj_x * cell_size + cell_size // 2
        y = proj_y * cell_size + cell_size // 2
        radius = 3
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            fill=color
        )
    
    # Draw snake
    for i, (snake_x, snake_y) in enumerate(game.state()['snake']):
        x = snake_x * cell_size
        y = snake_y * cell_size
        # Head is brighter green
        if i == 0:
            color = '#00FF00'
        else:
            color = '#00AA00'
        draw.rectangle(
            [x + 1, y + 1, x + cell_size - 1, y + cell_size - 1],
            fill=color
        )
    
    return img

def generate_gif(output_path: str = "dist/custom_snake.gif", num_steps: int = 200, cell_size: int = 15):
    """Generate an animated GIF of the custom snake game."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    game = Game()
    
    # Spawn colored dots across the grid
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'cyan', 'magenta']
    for i in range(15):
        x = random.randint(0, game.width - 1)
        y = random.randint(0, game.height - 1)
        color = random.choice(colors)
        game.spawn_dot(x, y, color)
    
    frames = []
    
    # Generate frames
    for step in range(num_steps):
        if game.is_game_over():
            print(f"Game over at step {step}!")
            break
        
        # Render current frame
        frame = render_frame(game, cell_size)
        frames.append(frame)
        
        # Update game state
        game.update()
        
        # Occasionally change snake direction
        if step % 20 == 0 and random.random() < 0.3:
            directions = [(1, 0), (0, 1), (0, -1)]
            game.snake.change_direction(random.choice(directions))
        
        # Spawn new dots occasionally
        if step % 30 == 0 and len(game.dots) < 20:
            x = random.randint(0, game.width - 1)
            y = random.randint(0, game.height - 1)
            color = random.choice(colors)
            game.spawn_dot(x, y, color)
    
    # Save as GIF
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,  # 100ms per frame
            loop=0
        )
        print(f"GIF saved to {output_path}")
        return output_path
    else:
        print("No frames generated!")
        return None

def main():
    import sys
    
    # Check if we should generate GIF or run demo
    if len(sys.argv) > 1 and sys.argv[1] == '--gif':
        output_path = sys.argv[2] if len(sys.argv) > 2 else "dist/custom_snake.gif"
        generate_gif(output_path)
    else:
        # Run a simple simulation printing the state each turn
        game = Game()
        # Spawn sample dots of different colors
        game.spawn_dot(10, 2, "red")
        game.spawn_dot(20, 4, "blue")
        game.spawn_dot(30, 1, "green")
        
        for step in range(50):
            if game.is_game_over():
                print(f"Game over at step {step}!")
                break
            game.update()
            print(f"Step {step}:", game.state())

if __name__ == "__main__":
    main()
