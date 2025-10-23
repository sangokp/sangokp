from PIL import Image, ImageDraw
import random, math

# Grid dimensions
width, height = 53, 7
cell = 10
frames_total = 120  # more frames for smoother animation

# Agent, projectile classes
class Agent:
    def __init__(self, name, x, y, color, behavior):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.behavior = behavior
        self.cooldown = 0
        self.has_projectile = False  # track bullet usage

class Projectile:
    def __init__(self, x, y, dx, dy, color, shooter, life=100):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.color = color
        self.shooter = shooter
        self.life = life

# Define your agents with colors/behaviors
agents = [
    Agent("Atlas", 10, 2, "#FFD700", "steady"),
    Agent("Hermes",25, 5, "#1E90FF", "rapid"),
    Agent("Encrypt",40, 1, "#8A2BE2", "teleport"),
    Agent("Sentinel",35, 6, "#DC143C", "precise"),
    Agent("Mnemosyne",15, 4, "#00FF7F", "diagonal"),
]

projectiles = []

# Snake initialisation
snake = [(5 - i, 3) for i in range(6)]
snake_dir = (1, 0)

def draw_frame():
    img = Image.new("RGB", (width * cell, height * cell), "black")
    draw = ImageDraw.Draw(img)

    # draw agents
    for agent in agents:
        draw.rectangle([(agent.x * cell, agent.y * cell),
                        ((agent.x + 1) * cell - 1, (agent.y + 1) * cell - 1)],
                       fill=agent.color)
    # draw projectiles
    for p in projectiles:
        draw.rectangle([(p.x * cell + cell // 4, p.y * cell + cell // 4),
                        (p.x * cell + 3 * cell // 4 - 1, p.y * cell + 3 * cell // 4 - 1)],
                       fill=p.color)

    # draw snake with white-to-grey gradient
    for i, (sx, sy) in enumerate(snake):
        c = max(255 - i * 20, 0)
        draw.rectangle([(sx * cell, sy * cell),
                        ((sx + 1) * cell - 1, (sy + 1) * cell - 1)],
                       fill=(c, c, c))
    return img

def move_agent(agent):
    if agent.behavior == "steady":
        agent.x = (agent.x + random.choice([-1, 0, 1])) % width
    elif agent.behavior == "rapid":
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        agent.x, agent.y = (agent.x + dx) % width, (agent.y + dy) % height
    elif agent.behavior == "teleport" and random.random() < 0.1:
        agent.x, agent.y = random.randint(0, width - 1), random.randint(0, height - 1)
    elif agent.behavior == "diagonal":
        agent.x, agent.y = (agent.x + 1) % width, (agent.y + 1) % height
    # Sentinel rarely moves

def agent_fire(agent):
    # Only fire if not cooling down and no active projectile
    if agent.cooldown > 0:
        agent.cooldown -= 1
        return
    if agent.has_projectile:
        return

    chance = {
        "steady": 0.07,
        "rapid": 0.15,
        "teleport": 0.08,
        "precise": 0.05,
        "diagonal": 0.1,
    }[agent.behavior]

    if random.random() < chance:
        head_x, head_y = snake[0]
        dx, dy = head_x - agent.x, head_y - agent.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            ux, uy = int(round(dx / dist)), int(round(dy / dist))
            proj = Projectile(agent.x, agent.y, ux, uy, agent.color, shooter=agent, life=100)
            projectiles.append(proj)
            agent.has_projectile = True
            agent.cooldown = 5

frames = []
for _ in range(frames_total):
    # update agents
    for a in agents:
        move_agent(a)
        agent_fire(a)

    # update projectiles
    for p in list(projectiles):
        p.x = (p.x + p.dx) % width
        p.y = (p.y + p.dy) % height
        p.life -= 1
        # remove projectile if it hits snake or life expires
        if (p.x, p.y) == snake[0] or p.life <= 0:
            p.shooter.has_projectile = False
            projectiles.remove(p)

    # occasionally change snake direction randomly
    if random.random() < 0.05:
        snake_dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
    head_x, head_y = snake[0]
    new_head = ((head_x + snake_dir[0]) % width, (head_y + snake_dir[1]) % height)
    snake.insert(0, new_head)
    snake.pop()

    # collision: snake absorbs agent & grows
    for a in agents:
        if (a.x, a.y) == new_head:
            snake.append(snake[-1])

    frames.append(draw_frame())

# Save GIF with shorter duration for smoother playback (e.g., 80 ms)
frames[0].save(
    "custom_snake.gif",
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True,
)
print("Created custom_snake.gif")
