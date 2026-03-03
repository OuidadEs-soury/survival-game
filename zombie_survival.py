import pygame
import random
import math

pygame.init()

# Window
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival - Level 2")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 60)

# Player
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_health = 100

# Score
score = 0

# Bullets
bullets = []
bullet_speed = 12
last_shot = 0
shoot_delay = 300  # milliseconds

# Zombies
zombies = []
zombie_base_speed = 1.5

# Health packs
health_packs = []

game_over = False


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

    zombies.append({
        "pos": [x, y],
        "speed": zombie_base_speed + score * 0.01
    })


def spawn_health_pack():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    health_packs.append([x, y])


def move_zombies():
    global player_health

    for zombie in zombies:
        dx = player_pos[0] - zombie["pos"][0]
        dy = player_pos[1] - zombie["pos"][1]
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        zombie["pos"][0] += dx * zombie["speed"]
        zombie["pos"][1] += dy * zombie["speed"]

        if math.hypot(player_pos[0] - zombie["pos"][0],
                      player_pos[1] - zombie["pos"][1]) < 20:
            player_health -= 0.5


def move_bullets():
    for bullet in bullets[:]:
        bullet[0] += bullet[2] * bullet_speed
        bullet[1] += bullet[3] * bullet_speed

        if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
            bullets.remove(bullet)


def check_collisions():
    global score

    for bullet in bullets[:]:
        for zombie in zombies[:]:
            if math.hypot(bullet[0] - zombie["pos"][0],
                          bullet[1] - zombie["pos"][1]) < 20:
                if bullet in bullets:
                    bullets.remove(bullet)
                if zombie in zombies:
                    zombies.remove(zombie)
                    score += 10


def check_health_pickup():
    global player_health
    for pack in health_packs[:]:
        if math.hypot(player_pos[0] - pack[0],
                      player_pos[1] - pack[1]) < 25:
            player_health = min(100, player_health + 25)
            health_packs.remove(pack)


def draw():
    screen.fill((15, 15, 20))

    # Player
    pygame.draw.circle(screen, (0, 200, 255), player_pos, 15)

    # Zombies
    for zombie in zombies:
        pygame.draw.circle(screen, (0, 180, 0),
                           (int(zombie["pos"][0]), int(zombie["pos"][1])), 15)

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0),
                           (int(bullet[0]), int(bullet[1])), 5)

    # Health packs
    for pack in health_packs:
        pygame.draw.rect(screen, (255, 0, 0),
                         (pack[0] - 10, pack[1] - 10, 20, 20))

    # UI
    health_text = font.render(f"Health: {int(player_health)}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))

    screen.blit(health_text, (20, 20))
    screen.blit(score_text, (20, 60))

    if game_over:
        over_text = big_font.render("GAME OVER", True, (255, 50, 50))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))

        screen.blit(over_text, (WIDTH // 2 - 180, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - 110, HEIGHT // 2 + 20))

    pygame.display.update()


spawn_timer = 0
health_timer = 0
running = True

while running:
    dt = clock.tick(60)
    spawn_timer += dt
    health_timer += dt

    if not game_over:

        if spawn_timer > 1000:
            spawn_zombie()
            spawn_timer = 0

        if health_timer > 10000:
            spawn_health_pack()
            health_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot > shoot_delay:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dx = mouse_x - player_pos[0]
                    dy = mouse_y - player_pos[1]
                    distance = math.hypot(dx, dy)

                    if distance != 0:
                        dx /= distance
                        dy /= distance

                    bullets.append([player_pos[0], player_pos[1], dx, dy])
                    last_shot = current_time

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
        check_health_pickup()

        if player_health <= 0:
            game_over = True

    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reset game
            player_health = 100
            score = 0
            zombies.clear()
            bullets.clear()
            health_packs.clear()
            player_pos = [WIDTH // 2, HEIGHT // 2]
            game_over = False

    draw()

pygame.quit()