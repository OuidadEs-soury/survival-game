import pygame
import random
import math

pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")

clock = pygame.time.Clock()

# Player settings
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_health = 100

# Bullet settings
bullets = []
bullet_speed = 10

# Zombie settings
zombies = []
zombie_speed = 2

# Font
font = pygame.font.SysFont("Arial", 24)

def spawn_zombie():
    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x = random.randint(0, WIDTH)
        y = 0
    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT
    elif side == "left":
        x = 0
        y = random.randint(0, HEIGHT)
    else:
        x = WIDTH
        y = random.randint(0, HEIGHT)

    zombies.append([x, y])

def move_zombies():
    global player_health
    for zombie in zombies[:]:
        dx = player_pos[0] - zombie[0]
        dy = player_pos[1] - zombie[1]
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        zombie[0] += dx * zombie_speed
        zombie[1] += dy * zombie_speed

        # Collision with player
        if math.hypot(player_pos[0] - zombie[0], player_pos[1] - zombie[1]) < 20:
            player_health -= 1

def move_bullets():
    for bullet in bullets[:]:
        bullet[0] += bullet[2] * bullet_speed
        bullet[1] += bullet[3] * bullet_speed

        if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
            bullets.remove(bullet)

def check_collisions():
    global zombies
    for bullet in bullets[:]:
        for zombie in zombies[:]:
            if math.hypot(bullet[0] - zombie[0], bullet[1] - zombie[1]) < 20:
                if bullet in bullets:
                    bullets.remove(bullet)
                if zombie in zombies:
                    zombies.remove(zombie)

def draw():
    screen.fill((20, 20, 20))

    # Player
    pygame.draw.circle(screen, (0, 200, 255), player_pos, 15)

    # Zombies
    for zombie in zombies:
        pygame.draw.circle(screen, (0, 200, 0), (int(zombie[0]), int(zombie[1])), 15)

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 5)

    # Health
    health_text = font.render(f"Health: {player_health}", True, (255, 255, 255))
    screen.blit(health_text, (10, 10))

    pygame.display.update()

spawn_timer = 0
running = True

while running:
    clock.tick(60)
    spawn_timer += 1

    if spawn_timer > 60:
        spawn_zombie()
        spawn_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_pos[0]
            dy = mouse_y - player_pos[1]
            distance = math.hypot(dx, dy)

            if distance != 0:
                dx /= distance
                dy /= distance

            bullets.append([player_pos[0], player_pos[1], dx, dy])

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos[1] -= player_speed
    if keys[pygame.K_s]:
        player_pos[1] += player_speed
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d]:
        player_pos[0] += player_speed

    move_zombies()
    move_bullets()
    check_collisions()
    draw()

    if player_health <= 0:
        running = False

pygame.quit()