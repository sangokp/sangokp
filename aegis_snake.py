#!/usr/bin/env python3
"""
AEGIS Snake Hunt - GitHub Profile Animation
A visually striking snake game animation for GitHub profile README.
AEGIS OS agents defend against a digital serpent threat.
"""
from PIL import Image, ImageDraw, ImageFilter
import random
import math

# ============================================================================
# CONFIGURATION
# ============================================================================

# Grid dimensions (optimized for GitHub README width ~830px)
WIDTH, HEIGHT = 83, 7
CELL_SIZE = 10
TOTAL_FRAMES = 180
FRAME_DURATION = 50  # milliseconds

# AEGIS Brand Colors
COLORS = {
    'background': (15, 15, 25),       # Deep space black
    'grid_line': (30, 30, 45),        # Subtle grid
    'snake_head': (180, 50, 50),      # Threat red
    'snake_body': (120, 35, 35),      # Darker red
    'snake_tail': (80, 25, 25),       # Fading red
    'projectile': (255, 215, 0),      # Gold bullet
    'particle': (255, 255, 200),      # Spark
    'text': (200, 200, 210),          # UI text
}

# Agent definitions with AEGIS department colors
AGENTS = [
    {'name': 'Thea', 'color': (255, 215, 0), 'glow': (255, 200, 50), 'behavior': 'commander'},
    {'name': 'Sentinel', 'color': (220, 50, 50), 'glow': (255, 80, 80), 'behavior': 'guardian'},
    {'name': 'Forge', 'color': (50, 180, 255), 'glow': (100, 200, 255), 'behavior': 'builder'},
    {'name': 'Atlas', 'color': (50, 220, 100), 'glow': (80, 255, 130), 'behavior': 'tracker'},
]

# ============================================================================
# GAME CLASSES
# ============================================================================

class Agent:
    def __init__(self, name, x, y, color, glow, behavior):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.glow = glow
        self.behavior = behavior
        self.cooldown = 0
        self.active_projectile = None
        self.pulse_phase = random.uniform(0, math.pi * 2)

    def get_pulse_intensity(self, frame):
        """Calculate pulsing glow intensity"""
        return 0.7 + 0.3 * math.sin(self.pulse_phase + frame * 0.15)


class Projectile:
    def __init__(self, x, y, dx, dy, color, shooter):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.shooter = shooter
        self.life = 150
        self.trail = []  # Store previous positions for trail effect

    def update_trail(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)


class Particle:
    def __init__(self, x, y, dx, dy, color, life=20):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.life = life
        self.max_life = life


# ============================================================================
# GAME STATE
# ============================================================================

agents = []
projectiles = []
particles = []
snake = []
snake_dir = (1, 0)
score = 0

def init_game():
    global agents, projectiles, particles, snake, snake_dir, score

    # Initialize agents at strategic positions
    positions = [
        (15, 3), (35, 2), (55, 4), (75, 3)
    ]
    agents = []
    for i, agent_def in enumerate(AGENTS):
        x, y = positions[i]
        agents.append(Agent(
            name=agent_def['name'],
            x=x, y=y,
            color=agent_def['color'],
            glow=agent_def['glow'],
            behavior=agent_def['behavior']
        ))

    projectiles = []
    particles = []

    # Initialize snake
    snake = [(5 - i, 3) for i in range(8)]
    snake_dir = (1, 0)
    score = 0


# ============================================================================
# DRAWING FUNCTIONS
# ============================================================================

def draw_glow_circle(draw, cx, cy, radius, color, intensity=1.0):
    """Draw a soft glow effect"""
    for r in range(int(radius), 0, -1):
        alpha = int(40 * intensity * (r / radius))
        glow_color = tuple(min(255, int(c * intensity)) for c in color)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=glow_color
        )


def draw_agent(draw, agent, frame):
    """Draw an agent with shield-like appearance and glow"""
    cx = agent.x * CELL_SIZE + CELL_SIZE // 2
    cy = agent.y * CELL_SIZE + CELL_SIZE // 2
    pulse = agent.get_pulse_intensity(frame)

    # Outer glow
    draw_glow_circle(draw, cx, cy, CELL_SIZE * 1.2, agent.glow, pulse * 0.4)

    # Diamond shape (AEGIS shield)
    size = CELL_SIZE // 2 - 1
    diamond = [
        (cx, cy - size),      # Top
        (cx + size, cy),      # Right
        (cx, cy + size),      # Bottom
        (cx - size, cy),      # Left
    ]

    # Fill with gradient-like effect
    draw.polygon(diamond, fill=agent.color, outline=agent.glow)

    # Inner highlight
    inner_size = size // 2
    inner_diamond = [
        (cx, cy - inner_size),
        (cx + inner_size, cy),
        (cx, cy + inner_size),
        (cx - inner_size, cy),
    ]
    highlight = tuple(min(255, c + 60) for c in agent.color)
    draw.polygon(inner_diamond, fill=highlight)


def draw_snake(draw, frame):
    """Draw snake with gradient and glow effects"""
    if not snake:
        return

    # Draw body segments from tail to head
    for i, (sx, sy) in enumerate(reversed(snake)):
        segment_idx = len(snake) - 1 - i
        cx = sx * CELL_SIZE + CELL_SIZE // 2
        cy = sy * CELL_SIZE + CELL_SIZE // 2

        # Calculate color gradient (head is brightest)
        progress = segment_idx / max(len(snake) - 1, 1)
        r = int(COLORS['snake_tail'][0] + (COLORS['snake_head'][0] - COLORS['snake_tail'][0]) * (1 - progress))
        g = int(COLORS['snake_tail'][1] + (COLORS['snake_head'][1] - COLORS['snake_tail'][1]) * (1 - progress))
        b = int(COLORS['snake_tail'][2] + (COLORS['snake_head'][2] - COLORS['snake_tail'][2]) * (1 - progress))

        # Size varies slightly along body
        size = CELL_SIZE // 2 - 1 + (2 if segment_idx == 0 else 0)

        # Draw segment
        draw.ellipse(
            [cx - size, cy - size, cx + size, cy + size],
            fill=(r, g, b)
        )

        # Head has special glow
        if segment_idx == 0:
            # Pulsing threat glow
            pulse = 0.6 + 0.4 * math.sin(frame * 0.2)
            draw_glow_circle(draw, cx, cy, CELL_SIZE, (255, 100, 100), pulse * 0.3)

            # Eyes
            eye_offset = 2
            if snake_dir[0] > 0:  # Moving right
                draw.ellipse([cx + eye_offset - 1, cy - 2, cx + eye_offset + 1, cy], fill=(255, 255, 200))
                draw.ellipse([cx + eye_offset - 1, cy + 1, cx + eye_offset + 1, cy + 3], fill=(255, 255, 200))
            elif snake_dir[0] < 0:  # Moving left
                draw.ellipse([cx - eye_offset - 1, cy - 2, cx - eye_offset + 1, cy], fill=(255, 255, 200))
                draw.ellipse([cx - eye_offset - 1, cy + 1, cx - eye_offset + 1, cy + 3], fill=(255, 255, 200))
            elif snake_dir[1] != 0:  # Moving vertically
                draw.ellipse([cx - 2, cy - 1, cx, cy + 1], fill=(255, 255, 200))
                draw.ellipse([cx + 1, cy - 1, cx + 3, cy + 1], fill=(255, 255, 200))


def draw_projectile(draw, proj):
    """Draw projectile with trail effect"""
    # Draw trail
    for i, (tx, ty) in enumerate(proj.trail):
        alpha = (i + 1) / len(proj.trail) if proj.trail else 1
        size = int(2 * alpha)
        tcx = tx * CELL_SIZE + CELL_SIZE // 2
        tcy = ty * CELL_SIZE + CELL_SIZE // 2
        trail_color = tuple(int(c * alpha * 0.5) for c in proj.color)
        draw.ellipse([tcx - size, tcy - size, tcx + size, tcy + size], fill=trail_color)

    # Draw main projectile
    cx = proj.x * CELL_SIZE + CELL_SIZE // 2
    cy = proj.y * CELL_SIZE + CELL_SIZE // 2

    # Glow
    draw_glow_circle(draw, cx, cy, 6, proj.color, 0.5)

    # Core
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=proj.color)

    # Bright center
    draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255))


def draw_particle(draw, particle):
    """Draw explosion/spark particle"""
    alpha = particle.life / particle.max_life
    size = int(3 * alpha)
    color = tuple(int(c * alpha) for c in particle.color)

    cx = int(particle.x * CELL_SIZE + CELL_SIZE // 2)
    cy = int(particle.y * CELL_SIZE + CELL_SIZE // 2)

    draw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=color)


def draw_grid(draw):
    """Draw subtle grid lines"""
    for x in range(0, WIDTH * CELL_SIZE, CELL_SIZE * 5):
        draw.line([(x, 0), (x, HEIGHT * CELL_SIZE)], fill=COLORS['grid_line'], width=1)
    for y in range(0, HEIGHT * CELL_SIZE, CELL_SIZE):
        draw.line([(0, y), (WIDTH * CELL_SIZE, y)], fill=COLORS['grid_line'], width=1)


def draw_frame(frame_num):
    """Draw a complete frame"""
    img = Image.new("RGB", (WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE), COLORS['background'])
    draw = ImageDraw.Draw(img)

    # Grid
    draw_grid(draw)

    # Particles (behind everything)
    for p in particles:
        draw_particle(draw, p)

    # Projectiles
    for proj in projectiles:
        draw_projectile(draw, proj)

    # Snake
    draw_snake(draw, frame_num)

    # Agents (on top)
    for agent in agents:
        draw_agent(draw, agent, frame_num)

    return img


# ============================================================================
# GAME LOGIC
# ============================================================================

def move_agent(agent):
    """Move agent based on behavior type"""
    if agent.behavior == 'commander':
        # Thea: Strategic positioning, stays central
        if random.random() < 0.3:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            agent.x = max(10, min(WIDTH - 10, agent.x + dx))
            agent.y = max(1, min(HEIGHT - 2, agent.y + dy))

    elif agent.behavior == 'guardian':
        # Sentinel: Patrols edges
        if random.random() < 0.4:
            agent.x = (agent.x + random.choice([-1, 1])) % WIDTH
            if random.random() < 0.2:
                agent.y = max(0, min(HEIGHT - 1, agent.y + random.choice([-1, 1])))

    elif agent.behavior == 'builder':
        # Forge: Steady horizontal movement
        if random.random() < 0.35:
            agent.x = (agent.x + 1) % WIDTH
            if random.random() < 0.15:
                agent.y = max(0, min(HEIGHT - 1, agent.y + random.choice([-1, 1])))

    elif agent.behavior == 'tracker':
        # Atlas: Follows snake general area
        if snake and random.random() < 0.4:
            head_x, head_y = snake[0]
            dx = 1 if head_x > agent.x else -1 if head_x < agent.x else 0
            dy = 1 if head_y > agent.y else -1 if head_y < agent.y else 0
            # Don't get too close
            dist = math.hypot(head_x - agent.x, head_y - agent.y)
            if dist > 8:
                agent.x = (agent.x + dx) % WIDTH
                agent.y = max(0, min(HEIGHT - 1, agent.y + dy))


def agent_fire(agent):
    """Agent attempts to fire at snake"""
    if agent.cooldown > 0:
        agent.cooldown -= 1
        return

    if agent.active_projectile is not None:
        return

    if not snake:
        return

    head_x, head_y = snake[0]
    dist = math.hypot(head_x - agent.x, head_y - agent.y)

    # Fire chance based on distance and behavior
    fire_chance = {
        'commander': 0.08,
        'guardian': 0.12,
        'builder': 0.06,
        'tracker': 0.10,
    }.get(agent.behavior, 0.05)

    # Closer = more likely to fire
    if dist < 20:
        fire_chance *= 1.5

    if random.random() < fire_chance:
        # Calculate direction to snake head
        dx = head_x - agent.x
        dy = head_y - agent.y
        if dist > 0:
            # Normalize and round to grid movement
            ux = round(dx / dist)
            uy = round(dy / dist)
            if ux == 0 and uy == 0:
                ux = 1  # Default direction

            proj = Projectile(agent.x, agent.y, ux, uy, agent.color, agent)
            projectiles.append(proj)
            agent.active_projectile = proj
            agent.cooldown = 15

            # Spawn firing particles
            for _ in range(3):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(0.1, 0.3)
                particles.append(Particle(
                    agent.x, agent.y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    agent.glow,
                    life=10
                ))


def update_projectiles():
    """Update all projectiles"""
    global score

    for proj in list(projectiles):
        proj.update_trail()
        proj.x = (proj.x + proj.dx) % WIDTH
        proj.y = (proj.y + proj.dy) % HEIGHT
        proj.life -= 1

        # Check collision with snake
        hit = False
        if snake and (proj.x, proj.y) == snake[0]:
            hit = True
            score += 1
            # Spawn hit particles
            for _ in range(8):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(0.2, 0.5)
                particles.append(Particle(
                    proj.x, proj.y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    COLORS['particle'],
                    life=15
                ))

        # Remove expired or hit projectiles
        if proj.life <= 0 or hit:
            if proj.shooter:
                proj.shooter.active_projectile = None
            projectiles.remove(proj)


def update_particles():
    """Update particle effects"""
    for p in list(particles):
        p.x += p.dx
        p.y += p.dy
        p.life -= 1
        if p.life <= 0:
            particles.remove(p)


def update_snake():
    """Update snake movement"""
    global snake_dir

    if not snake:
        return

    # Random direction changes (wandering behavior)
    if random.random() < 0.06:
        possible_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        # Avoid immediate reversal
        opposite = (-snake_dir[0], -snake_dir[1])
        possible_dirs = [d for d in possible_dirs if d != opposite]
        snake_dir = random.choice(possible_dirs)

    # Move snake
    head_x, head_y = snake[0]
    new_head = ((head_x + snake_dir[0]) % WIDTH, (head_y + snake_dir[1]) % HEIGHT)
    snake.insert(0, new_head)
    snake.pop()

    # Check if snake eats an agent
    for agent in agents:
        if (agent.x, agent.y) == new_head:
            # Snake grows
            snake.append(snake[-1])
            snake.append(snake[-1])

            # Respawn agent
            agent.x = random.randint(10, WIDTH - 10)
            agent.y = random.randint(1, HEIGHT - 2)
            agent.active_projectile = None
            agent.cooldown = 20

            # Spawn "eaten" particles
            for _ in range(12):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(0.3, 0.6)
                particles.append(Particle(
                    new_head[0], new_head[1],
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    agent.glow,
                    life=20
                ))


# ============================================================================
# MAIN
# ============================================================================

def main():
    init_game()
    frames = []

    for frame_num in range(TOTAL_FRAMES):
        # Update game state
        for agent in agents:
            move_agent(agent)
            agent_fire(agent)

        update_projectiles()
        update_particles()
        update_snake()

        # Draw frame
        frames.append(draw_frame(frame_num))

    # Save animation
    frames[0].save(
        'aegis_snake.gif',
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=True
    )
    print(f'Created aegis_snake.gif ({len(frames)} frames, {FRAME_DURATION}ms/frame)')


if __name__ == '__main__':
    main()
