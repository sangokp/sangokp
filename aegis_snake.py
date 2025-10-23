from PIL import Image, ImageDraw
import random, math

# Grid dimensions: combine two 53x7 grids into one 106x7 grid
width, height = 106, 7
cell = 10
frames_total = 120  # number of frames for smooth animation

# Agent, projectile classes
class Agent:
    def __init__(self, name, x, y, color, behavior):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.behavior = behavior
        self.cooldown = 0
        self.has_projectile = False  # track whether agent has active bullet

class Projectile:
    def __init__(self, x, y, dx, dy, color, shooter, life=200):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.shooter = shooter
        self.life = life

# Define a small set of agents at various positions with different behaviors
agents = [
    Agent("Atlas", 20, 3, "#FFD700", "steady"),   # moves slowly horizontally
    Agent("Hermes", 60, 2, "#1E90FF", "rapid"),  # moves more often
    Agent("Mnemosyne", 90, 4, "#00FF7F", "diagonal")  # moves diagonally
]

projectiles = []

# Snake initial state: a single snake across new grid; start near left center
snake = [(5 - i, 3) for i in range(6)]
# initial direction to the right
snake_dir = (1, 0)

def draw_frame():
    """Draw one frame of the game."""
    img = Image.new("RGB", (width * cell, height * cell), "black")
    draw = ImageDraw.Draw(img)

    # Draw agents as colored squares
    for agent in agents:
        draw.rectangle([(agent.x * cell, agent.y * cell),
                        ((agent.x + 1) * cell - 1, (agent.y + 1) * cell - 1)],
                       fill=agent.color)

    # Draw projectiles as small colored squares
    for p in projectiles:
        draw.rectangle([(p.x * cell + cell // 4, p.y * cell + cell // 4),
                        (p.x * cell + 3 * cell // 4 - 1, p.y * cell + 3 * cell // 4 - 1)],
                       fill=p.color)

    # Draw snake with a white to grey gradient tail (head is white)
    for i, (sx, sy) in enumerate(snake):
        # gradient from white to dark grey
        c = max(255 - i * 20, 50)  # ensure some tail brightness
        draw.rectangle([(sx * cell, sy * cell),
                        ((sx + 1) * cell - 1, (sy + 1) * cell - 1)],
                       fill=(c, c, c))

    return img

def move_agent(agent):
    """Move agent based on its behavior."""
    if agent.behavior == "steady":
        # move horizontally with occasional vertical move
        move_choice = random.choice([(-1,0), (1,0), (0,0), (0,0), (0,1), (0,-1)])
        agent.x = (agent.x + move_choice[0]) % width
        agent.y = (agent.y + move_choice[1]) % height
    elif agent.behavior == "rapid":
        # move in any direction each frame
        dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        agent.x = (agent.x + dx) % width
        agent.y = (agent.y + dy) % height
    elif agent.behavior == "diagonal":
        # always move diagonally
        agent.x = (agent.x + 1) % width
        agent.y = (agent.y + 1) % height

def is_snake_moving_towards(agent, head, direction):
    """Determine if the snake is moving towards the agent.
    We compare the direction vector from snake head to agent with the snake's movement direction.
    If the dot product of the unit direction vector and snake direction is positive, it's moving towards the agent.
    """
    dx = agent.x - head[0]
    dy = agent.y - head[1]
    # if the distance is zero, return True to allow shooting (though improbable)
    if dx == 0 and dy == 0:
        return True
    # convert to unit vector for direction to agent
    # get signs
    sign_dx = 0 if dx == 0 else (1 if dx > 0 else -1)
    sign_dy = 0 if dy == 0 else (1 if dy > 0 else -1)
    # dot product with snake direction
    return (sign_dx * direction[0] + sign_dy * direction[1]) > 0

def agent_fire(agent):
    """Agent fires a projectile if conditions are met."""
    if agent.cooldown > 0:
        agent.cooldown -= 1
        return
    if agent.has_projectile:
        return
    # Determine if snake is moving towards this agent
    head_x, head_y = snake[0]
    if not is_snake_moving_towards(agent, (head_x, head_y), snake_dir):
        return

    # Chance to shoot; set low to reduce bullets
    # Variation by agent type
    chance = {
        "steady": 0.05,
        "rapid": 0.08,
        "diagonal": 0.06
    }[agent.behavior]
    if random.random() < chance:
        # compute unit vector towards snake head
        dx = head_x - agent.x
        dy = head_y - agent.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        ux = int(round(dx / dist))
        uy = int(round(dy / dist))
        proj = Projectile(agent.x, agent.y, ux, uy, agent.color, shooter=agent, life=200)
        projectiles.append(proj)
        agent.has_projectile = True
        # set cooldown to avoid repeated shooting
        agent.cooldown = 10

def update_projectiles():
    for p in list(projectiles):
        # move projectile
        p.x = (p.x + p.dx) % width
        p.y = (p.y + p.dy) % height
        p.life -= 1
        # check collision with snake head or expire
        if (p.x, p.y) == snake[0] or p.life <= 0:
            # release shooter bullet state
            p.shooter.has_projectile = False
            projectiles.remove(p)

def update_snake():
    global snake_dir
    # Randomly change direction sometimes to wander
    if random.random() < 0.04:
        snake_dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
    # Move snake head
    head_x, head_y = snake[0]
    new_head = ((head_x + snake_dir[0]) % width, (head_y + snake_dir[1]) % height)
    # insert new head
    snake.insert(0, new_head)
    # remove tail
    snake.pop()
    # check if snake eats agent
    for agent in agents:
        if (agent.x, agent.y) == new_head:
            # grow snake by repeating last segment
            snake.append(snake[-1])
            # respawn agent to random location
            agent.x = random.randint(0, width - 1)
            agent.y = random.randint(0, height - 1)
            agent.has_projectile = False
            agent.cooldown = 0

frames = []
for _ in range(frames_total):
    # update agents and maybe fire
    for agent in agents:
        move_agent(agent)
        agent_fire(agent)
    # update projectiles
    update_projectiles()
    # update snake
    update_snake()
    # draw frame
    frames.append(draw_frame())

# Save the animation as GIF
frames[0].save(
    'custom_snake.gif',
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True
)
print('Created custom_snake.gif')
