import pygame
import random
import math
import os

pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except:
    print("Sound disabled.")
    sound_enabled = False

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival - Apocalypse")

clock = pygame.time.Clock()

# Load assets
background = pygame.image.load("assets/background.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

if sound_enabled:
    shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    hit_sound = pygame.mixer.Sound("assets/hit.wav")
else:
    shoot_sound = None
    hit_sound = None

font = pygame.font.SysFont("Arial", 28)
big_font = pygame.font.SysFont("Arial", 70)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
state = MENU

# Player
player_pos = [WIDTH // 2, HEIGHT // 2]
player_speed = 5
player_health = 100
dash_cooldown = 0

# Score
score = 0

# Weapons
weapon_mode = 1  # 1 = pistol, 2 = shotgun

# Bullets
bullets = []
bullet_speed = 14
shoot_delay = 300
last_shot = 0

# Zombies
zombies = []
zombie_speed = 1.5

# Boss
boss_active = False

# Explosions
explosions = []


def spawn_zombie():
    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x, y = random.randint(0, WIDTH), 0
    elif side == "bottom":
        x, y = random.randint(0, WIDTH), HEIGHT
    elif side == "left":
        x, y = 0, random.randint(0, HEIGHT)
    else:
        x, y = WIDTH, random.randint(0, HEIGHT)

    zombies.append({
        "pos": [x, y],
        "speed": zombie_speed + score * 0.005,
        "health": 1,
        "boss": False
    })


def spawn_boss():
    global boss_active
    zombies.append({
        "pos": [random.randint(100, WIDTH - 100),
                random.randint(100, HEIGHT - 100)],
        "speed": 1,
        "health": 15,
        "boss": True
    })
    boss_active = True


def shoot(target_x, target_y):
    global last_shot
    current_time = pygame.time.get_ticks()

    if current_time - last_shot < shoot_delay:
        return

    shoot_sound.play()
    dx = target_x - player_pos[0]
    dy = target_y - player_pos[1]
    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    dx /= distance
    dy /= distance

    if weapon_mode == 1:
        bullets.append([player_pos[0], player_pos[1], dx, dy])
    else:
        # Shotgun spread
        for angle in [-0.2, 0, 0.2]:
            new_dx = dx * math.cos(angle) - dy * math.sin(angle)
            new_dy = dx * math.sin(angle) + dy * math.cos(angle)
            bullets.append([player_pos[0], player_pos[1], new_dx, new_dy])

    last_shot = current_time


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

        if distance < 20:
            player_health -= 0.4


def move_bullets():
    for bullet in bullets[:]:
        bullet[0] += bullet[2] * bullet_speed
        bullet[1] += bullet[3] * bullet_speed

        if bullet[0] < 0 or bullet[0] > WIDTH or bullet[1] < 0 or bullet[1] > HEIGHT:
            bullets.remove(bullet)


def check_collisions():
    global score, boss_active

    for bullet in bullets[:]:
        for zombie in zombies[:]:
            if math.hypot(bullet[0] - zombie["pos"][0],
                          bullet[1] - zombie["pos"][1]) < 20:
                zombie["health"] -= 1
                if bullet in bullets:
                    bullets.remove(bullet)
                hit_sound.play()

                if zombie["health"] <= 0:
                    if zombie["boss"]:
                        score += 100
                        boss_active = False
                    else:
                        score += 10
                    explosions.append(zombie["pos"][:])
                    zombies.remove(zombie)


def draw_explosions():
    for exp in explosions[:]:
        pygame.draw.circle(screen, (255, 100, 0), exp, 30)
        explosions.remove(exp)


def draw():
    screen.blit(background, (0, 0))

    # Player
    pygame.draw.circle(screen, (0, 200, 255), player_pos, 15)

    # Zombies
    for zombie in zombies:
        color = (150, 0, 150) if zombie["boss"] else (0, 200, 0)
        pygame.draw.circle(screen, color,
                           (int(zombie["pos"][0]), int(zombie["pos"][1])), 18 if zombie["boss"] else 15)

    # Bullets
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0),
                           (int(bullet[0]), int(bullet[1])), 5)

    draw_explosions()

    # UI
    health_text = font.render(f"Health: {int(player_health)}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    weapon_text = font.render(f"Weapon: {'Shotgun' if weapon_mode == 2 else 'Pistol'}", True, (255, 255, 255))

    screen.blit(health_text, (20, 20))
    screen.blit(score_text, (20, 60))
    screen.blit(weapon_text, (20, 100))

    pygame.display.update()


def reset_game():
    global player_health, score, zombies, bullets, boss_active, state
    player_health = 100
    score = 0
    zombies.clear()
    bullets.clear()
    boss_active = False
    state = PLAYING


running = True
spawn_timer = 0

while running:
    dt = clock.tick(60)
    spawn_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if event.type == pygame.KEYDOWN:
                state = PLAYING

        elif state == PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                shoot(mx, my)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    weapon_mode = 1
                if event.key == pygame.K_2:
                    weapon_mode = 2
                if event.key == pygame.K_SPACE and dash_cooldown <= 0:
                    player_pos[0] += 100
                    dash_cooldown = 2000

        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()

    if state == MENU:
        screen.fill((0, 0, 0))
        title = big_font.render("ZOMBIE APOCALYPSE", True, (200, 0, 0))
        start = font.render("Press any key to start", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - 250, HEIGHT // 2 - 60))
        screen.blit(start, (WIDTH // 2 - 130, HEIGHT // 2 + 20))
        pygame.display.update()
        continue

    if state == PLAYING:

        if spawn_timer > 1200:
            spawn_zombie()
            spawn_timer = 0

        if score > 200 and not boss_active:
            spawn_boss()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_pos[1] -= player_speed
        if keys[pygame.K_s]:
            player_pos[1] += player_speed
        if keys[pygame.K_a]:
            player_pos[0] -= player_speed
        if keys[pygame.K_d]:
            player_pos[0] += player_speed

        if dash_cooldown > 0:
            dash_cooldown -= dt

        move_zombies()
        move_bullets()
        check_collisions()

        if player_health <= 0:
            state = GAME_OVER

        draw()

    elif state == GAME_OVER:
        screen.fill((20, 0, 0))
        over = big_font.render("GAME OVER", True, (255, 255, 255))
        restart = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(over, (WIDTH // 2 - 180, HEIGHT // 2 - 50))
        screen.blit(restart, (WIDTH // 2 - 120, HEIGHT // 2 + 20))
        pygame.display.update()

pygame.quit()