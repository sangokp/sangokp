#!/usr/bin/env python3
"""
AEGIS Constellation - GitHub Profile Animation
A swarm of intelligent agents demonstrating emergent coordination.
Each agent has distinct visual identity and purposeful behavior.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
from dataclasses import dataclass
from typing import List, Tuple
import colorsys

# ============================================================================
# CONFIGURATION
# ============================================================================

WIDTH = 830
HEIGHT = 180
TOTAL_FRAMES = 180  # Shorter loop, smaller file
FRAME_DURATION = 50  # ~20fps, still smooth
BACKGROUND = (8, 10, 18)  # Deep space

# Agent definitions with clear roles
AGENT_SPECS = {
    'thea': {
        'name': 'Thea',
        'role': 'Orchestrator',
        'color': (255, 215, 80),      # Bright Gold
        'glow': (255, 200, 60),
        'size': 12,                   # Larger, more prominent
        'count': 1,
        'behavior': 'leader',
    },
    'sentinel': {
        'name': 'Sentinel',
        'role': 'Security',
        'color': (220, 60, 80),       # Red
        'glow': (255, 80, 100),
        'size': 5,
        'count': 6,
        'behavior': 'guardian',
    },
    'forge': {
        'name': 'Forge',
        'role': 'Builder',
        'color': (60, 160, 255),      # Blue
        'glow': (80, 180, 255),
        'size': 5,
        'count': 8,
        'behavior': 'builder',
    },
    'atlas': {
        'name': 'Atlas',
        'role': 'Operations',
        'color': (60, 220, 120),      # Green
        'glow': (80, 255, 140),
        'size': 4,
        'count': 10,
        'behavior': 'connector',
    },
    'apollo': {
        'name': 'Apollo',
        'role': 'Design',
        'color': (180, 100, 255),     # Purple
        'glow': (200, 120, 255),
        'size': 4,
        'count': 6,
        'behavior': 'aesthetic',
    },
    'mnemosyne': {
        'name': 'Mnemosyne',
        'role': 'Memory',
        'color': (80, 220, 240),      # Cyan
        'glow': (100, 240, 255),
        'size': 3,
        'count': 8,
        'behavior': 'anchor',
    },
}

# Formation phases
PHASE_DURATION = 60  # frames per phase
PHASES = ['scatter', 'converge', 'orbit']

# ============================================================================
# AGENT CLASS
# ============================================================================

@dataclass
class Agent:
    x: float
    y: float
    vx: float
    vy: float
    agent_type: str
    index: int

    @property
    def spec(self):
        return AGENT_SPECS[self.agent_type]

    @property
    def color(self):
        return self.spec['color']

    @property
    def glow(self):
        return self.spec['glow']

    @property
    def size(self):
        return self.spec['size']

    @property
    def behavior(self):
        return self.spec['behavior']


# ============================================================================
# BOIDS ALGORITHM (Modified for AEGIS)
# ============================================================================

def get_boid_forces(agent: Agent, all_agents: List[Agent], target: Tuple[float, float], phase: str) -> Tuple[float, float]:
    """Calculate steering forces based on behavior type and phase."""

    # Parameters vary by behavior
    params = {
        'leader': {'sep': 80, 'ali': 0.0, 'coh': 0.0, 'target': 0.02},
        'guardian': {'sep': 40, 'ali': 0.3, 'coh': 0.5, 'target': 0.01},
        'builder': {'sep': 30, 'ali': 0.5, 'coh': 0.8, 'target': 0.015},
        'connector': {'sep': 25, 'ali': 0.4, 'coh': 0.3, 'target': 0.02},
        'aesthetic': {'sep': 35, 'ali': 0.6, 'coh': 0.4, 'target': 0.012},
        'anchor': {'sep': 50, 'ali': 0.2, 'coh': 0.2, 'target': 0.005},
    }

    p = params.get(agent.behavior, params['connector'])

    # Separation
    sep_x, sep_y = 0, 0
    # Alignment
    ali_x, ali_y = 0, 0
    ali_count = 0
    # Cohesion
    coh_x, coh_y = 0, 0
    coh_count = 0

    for other in all_agents:
        if other is agent:
            continue

        dx = agent.x - other.x
        dy = agent.y - other.y
        dist = math.sqrt(dx*dx + dy*dy) + 0.001

        # Separation (avoid crowding)
        if dist < p['sep']:
            sep_x += dx / dist
            sep_y += dy / dist

        # Alignment (match velocity of same type)
        if dist < 100 and other.agent_type == agent.agent_type:
            ali_x += other.vx
            ali_y += other.vy
            ali_count += 1

        # Cohesion (move toward center of flock)
        if dist < 150:
            coh_x += other.x
            coh_y += other.y
            coh_count += 1

    # Normalize alignment
    if ali_count > 0:
        ali_x = (ali_x / ali_count - agent.vx) * p['ali']
        ali_y = (ali_y / ali_count - agent.vy) * p['ali']

    # Normalize cohesion
    if coh_count > 0:
        coh_x = (coh_x / coh_count - agent.x) * 0.01 * p['coh']
        coh_y = (coh_y / coh_count - agent.y) * 0.01 * p['coh']

    # Target seeking (toward formation target)
    tar_x = (target[0] - agent.x) * p['target']
    tar_y = (target[1] - agent.y) * p['target']

    # Phase-specific modifications
    if phase == 'scatter':
        # More separation, less cohesion
        sep_x *= 2
        sep_y *= 2
        coh_x *= 0.3
        coh_y *= 0.3
    elif phase == 'orbit':
        # Add orbital motion around center
        cx, cy = WIDTH / 2, HEIGHT / 2
        dx = agent.x - cx
        dy = agent.y - cy
        dist = math.sqrt(dx*dx + dy*dy) + 0.001
        # Perpendicular force (orbit)
        orbit_strength = 0.15 if agent.behavior != 'anchor' else 0.05
        tar_x += (-dy / dist) * orbit_strength
        tar_y += (dx / dist) * orbit_strength

    # Combine forces
    fx = sep_x * 0.5 + ali_x + coh_x + tar_x
    fy = sep_y * 0.5 + ali_y + coh_y + tar_y

    return fx, fy


def get_formation_target(agent: Agent, frame: int, phase: str) -> Tuple[float, float]:
    """Get target position based on formation and agent role."""

    cx, cy = WIDTH / 2, HEIGHT / 2
    t = frame / TOTAL_FRAMES * math.pi * 4

    if agent.behavior == 'leader':
        # Thea: Center, slight movement
        return cx + math.sin(t * 0.3) * 30, cy + math.cos(t * 0.4) * 15

    elif agent.behavior == 'guardian':
        # Sentinel: Outer perimeter, scanning
        angle = (agent.index / 6) * math.pi * 2 + t * 0.5
        radius = 120 if phase == 'orbit' else 80
        return cx + math.cos(angle) * radius, cy + math.sin(angle) * radius * 0.4

    elif agent.behavior == 'builder':
        # Forge: Form structured patterns
        if phase == 'converge':
            # Form a grid-like structure
            row = agent.index // 4
            col = agent.index % 4
            return cx - 60 + col * 40, cy - 20 + row * 30
        else:
            angle = (agent.index / 8) * math.pi * 2 + t * 0.3
            return cx + math.cos(angle) * 70, cy + math.sin(angle) * 35

    elif agent.behavior == 'connector':
        # Atlas: Fast-moving connections
        angle = (agent.index / 10) * math.pi * 2 + t * 0.8
        radius = 50 + math.sin(t * 2 + agent.index) * 30
        return cx + math.cos(angle) * radius, cy + math.sin(angle) * radius * 0.5

    elif agent.behavior == 'aesthetic':
        # Apollo: Smooth, flowing paths
        wave = math.sin(t * 0.6 + agent.index * 0.5)
        return cx + wave * 100, cy + math.cos(t * 0.4 + agent.index) * 40

    elif agent.behavior == 'anchor':
        # Mnemosyne: Stable positions, slight drift
        base_x = 100 + (agent.index % 4) * 180
        base_y = 50 + (agent.index // 4) * 80
        return base_x + math.sin(t * 0.1 + agent.index) * 10, base_y


def update_agent(agent: Agent, all_agents: List[Agent], frame: int, phase: str):
    """Update agent position with smooth motion."""

    target = get_formation_target(agent, frame, phase)
    fx, fy = get_boid_forces(agent, all_agents, target, phase)

    # Apply forces with damping
    max_speed = 3.0 if agent.behavior == 'connector' else 2.0
    if agent.behavior == 'anchor':
        max_speed = 0.8

    agent.vx = agent.vx * 0.95 + fx
    agent.vy = agent.vy * 0.95 + fy

    # Limit speed
    speed = math.sqrt(agent.vx**2 + agent.vy**2)
    if speed > max_speed:
        agent.vx = agent.vx / speed * max_speed
        agent.vy = agent.vy / speed * max_speed

    # Update position
    agent.x += agent.vx
    agent.y += agent.vy

    # Soft boundaries
    margin = 30
    if agent.x < margin:
        agent.vx += 0.5
    elif agent.x > WIDTH - margin:
        agent.vx -= 0.5
    if agent.y < margin:
        agent.vy += 0.5
    elif agent.y > HEIGHT - margin:
        agent.vy -= 0.5


# ============================================================================
# RENDERING
# ============================================================================

def draw_connection_lines(draw: ImageDraw, agents: List[Agent], frame: int):
    """Draw subtle connection lines between related agents."""

    # Find Thea (leader)
    thea = next((a for a in agents if a.behavior == 'leader'), None)
    if not thea:
        return

    # Pulse effect
    pulse = 0.3 + 0.2 * math.sin(frame * 0.1)

    # Draw lines from connectors to nearby agents
    for agent in agents:
        if agent.behavior != 'connector':
            continue

        # Find closest non-connector agent
        closest = None
        closest_dist = float('inf')

        for other in agents:
            if other.behavior == 'connector' or other is agent:
                continue
            dist = math.sqrt((agent.x - other.x)**2 + (agent.y - other.y)**2)
            if dist < closest_dist and dist < 100:
                closest_dist = dist
                closest = other

        if closest:
            alpha = int(40 * pulse * (1 - closest_dist / 100))
            color = (60, 220, 120, alpha)
            draw.line([(agent.x, agent.y), (closest.x, closest.y)],
                     fill=(60, 180, 100), width=1)


def draw_agent_glow(img: Image, agent: Agent, frame: int):
    """Draw soft glow around agent."""

    # Create glow layer
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Pulse intensity
    pulse = 0.6 + 0.4 * math.sin(frame * 0.15 + agent.index * 0.5)

    # Draw multiple rings for soft glow
    for radius in range(agent.size * 4, agent.size, -2):
        alpha = int(20 * pulse * (1 - radius / (agent.size * 4)))
        r, g, b = agent.glow
        glow_draw.ellipse(
            [agent.x - radius, agent.y - radius,
             agent.x + radius, agent.y + radius],
            fill=(r, g, b, alpha)
        )

    return glow


def draw_agent_core(draw: ImageDraw, agent: Agent, frame: int):
    """Draw the agent's core shape."""

    size = agent.size
    x, y = agent.x, agent.y

    if agent.behavior == 'leader':
        # Thea: Diamond shape (command)
        points = [
            (x, y - size * 1.5),
            (x + size * 1.2, y),
            (x, y + size * 1.5),
            (x - size * 1.2, y),
        ]
        draw.polygon(points, fill=agent.color)
        # Inner highlight
        inner = [
            (x, y - size * 0.6),
            (x + size * 0.5, y),
            (x, y + size * 0.6),
            (x - size * 0.5, y),
        ]
        highlight = tuple(min(255, c + 60) for c in agent.color)
        draw.polygon(inner, fill=highlight)

    elif agent.behavior == 'guardian':
        # Sentinel: Triangle (shield/arrow)
        angle = math.atan2(agent.vy, agent.vx)
        points = [
            (x + math.cos(angle) * size * 1.5, y + math.sin(angle) * size * 1.5),
            (x + math.cos(angle + 2.5) * size, y + math.sin(angle + 2.5) * size),
            (x + math.cos(angle - 2.5) * size, y + math.sin(angle - 2.5) * size),
        ]
        draw.polygon(points, fill=agent.color)

    elif agent.behavior == 'builder':
        # Forge: Square (building block)
        draw.rectangle(
            [x - size, y - size, x + size, y + size],
            fill=agent.color
        )
        # Inner detail
        draw.rectangle(
            [x - size * 0.4, y - size * 0.4, x + size * 0.4, y + size * 0.4],
            fill=tuple(min(255, c + 50) for c in agent.color)
        )

    elif agent.behavior == 'connector':
        # Atlas: Small circle with motion trail effect
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=agent.color
        )
        # Motion indicator
        trail_x = x - agent.vx * 3
        trail_y = y - agent.vy * 3
        draw.line([(trail_x, trail_y), (x, y)], fill=agent.glow, width=2)

    elif agent.behavior == 'aesthetic':
        # Apollo: Soft circle with gradient feel
        draw.ellipse(
            [x - size * 1.2, y - size * 1.2, x + size * 1.2, y + size * 1.2],
            fill=agent.color
        )

    elif agent.behavior == 'anchor':
        # Mnemosyne: Hexagon (data/memory)
        points = []
        for i in range(6):
            angle = i * math.pi / 3 - math.pi / 6
            points.append((
                x + math.cos(angle) * size,
                y + math.sin(angle) * size
            ))
        draw.polygon(points, fill=agent.color)


def draw_frame(agents: List[Agent], frame: int, phase: str) -> Image:
    """Render a complete frame."""

    # Create base image
    img = Image.new('RGBA', (WIDTH, HEIGHT), (*BACKGROUND, 255))
    draw = ImageDraw.Draw(img)

    # Subtle grid pattern
    grid_color = (20, 25, 40)
    for x in range(0, WIDTH, 40):
        alpha = 0.3 + 0.1 * math.sin(frame * 0.05 + x * 0.01)
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(0, HEIGHT, 40):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    # Draw connection lines first (behind agents)
    draw_connection_lines(draw, agents, frame)

    # Composite glow layers
    glow_composite = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for agent in agents:
        glow = draw_agent_glow(img, agent, frame)
        glow_composite = Image.alpha_composite(glow_composite, glow)

    # Apply glow with blur
    glow_composite = glow_composite.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.alpha_composite(img, glow_composite)

    # Draw agent cores
    draw = ImageDraw.Draw(img)

    # Sort by y for depth effect
    sorted_agents = sorted(agents, key=lambda a: a.y)
    for agent in sorted_agents:
        draw_agent_core(draw, agent, frame)

    return img.convert('RGB')


# ============================================================================
# MAIN
# ============================================================================

def create_agents() -> List[Agent]:
    """Initialize all agents with starting positions."""

    agents = []

    for agent_type, spec in AGENT_SPECS.items():
        for i in range(spec['count']):
            # Random starting positions (will converge)
            x = random.uniform(50, WIDTH - 50)
            y = random.uniform(30, HEIGHT - 30)
            vx = random.uniform(-1, 1)
            vy = random.uniform(-0.5, 0.5)

            agents.append(Agent(
                x=x, y=y, vx=vx, vy=vy,
                agent_type=agent_type,
                index=i
            ))

    return agents


def main():
    print("Initializing AEGIS Constellation...")
    agents = create_agents()
    frames = []

    for frame_num in range(TOTAL_FRAMES):
        # Determine phase
        phase_idx = (frame_num // PHASE_DURATION) % len(PHASES)
        phase = PHASES[phase_idx]

        # Update all agents
        for agent in agents:
            update_agent(agent, agents, frame_num, phase)

        # Render frame
        img = draw_frame(agents, frame_num, phase)
        frames.append(img)

        if frame_num % 30 == 0:
            print(f"  Frame {frame_num}/{TOTAL_FRAMES} ({phase})")

    # Save animation
    print("Saving animation...")
    frames[0].save(
        'aegis_constellation.gif',
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=False  # Better quality
    )

    # Also save a preview frame
    frames[60].save('aegis_constellation_preview.png')

    print(f"Created aegis_constellation.gif")
    print(f"  {len(frames)} frames @ {FRAME_DURATION}ms = {len(frames) * FRAME_DURATION / 1000:.1f}s loop")
    print(f"  {WIDTH}x{HEIGHT} pixels")


if __name__ == '__main__':
    main()
