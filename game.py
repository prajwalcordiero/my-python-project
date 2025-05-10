import pygame
from pygame.locals import *

pygame.init()

# --- Settings ---
tile_size = 50
screen_width = 800
screen_height = 800
fps = 60

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

clock = pygame.time.Clock()

# --- Load images ---
bg_img = pygame.image.load('sky1.png')
coin_img = pygame.image.load('coin.png')
health_img = pygame.image.load('health.png')
enemy_img = pygame.image.load('enemy.png')

# --- Grid Drawing Function ---
# def draw_grid():
#     for line in range(0, screen_height // tile_size + 1):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#     for line in range(0, screen_width // tile_size + 1):
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))

# --- Player Class ---
class Player():
    def __init__(self, x, y):
        img = pygame.image.load('guy.png')
        self.image = pygame.transform.scale(img, (80, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.health = 3
        self.score = 0

    def update(self, world):
        dx = 0
        dy = 0

        # --- Movement ---
        key = pygame.key.get_pressed()
        if key[K_SPACE] and not self.jumped:
            self.vel_y = -15
            self.jumped = True
        if key[K_LEFT]:
            dx = -5
        if key[K_RIGHT]:
            dx = 5

        # --- Gravity ---
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # --- Collision with platforms (top surface only) ---
        for tile in world.tile_list:
            tile_rect = tile[1]

            if self.rect.bottom + dy > tile_rect.top and self.rect.bottom <= tile_rect.top + 10 and \
               self.rect.right > tile_rect.left + 5 and self.rect.left < tile_rect.right - 5:
                dy = tile_rect.top - self.rect.bottom
                self.vel_y = 0
                self.jumped = False

        # --- Apply movement ---
        self.rect.x += dx
        self.rect.y += dy

        # --- Border collision (stay inside screen) ---
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.vel_y = 0
            self.jumped = False

        # --- Draw player ---
        screen.blit(self.image, self.rect)

    def check_collision(self, enemy):
        if self.rect.colliderect(enemy.rect):
            self.health -= 1
            self.rect.x = 100
            self.rect.y = screen_height - tile_size * 3
            enemy.reset()

    def check_coins(self, coins):
        for coin in coins[:]:
            if self.rect.colliderect(coin):
                self.score += 1
                coins.remove(coin)

    def check_exit(self, exit_rect):
        return self.rect.colliderect(exit_rect)

# --- Enemy Class ---
class Enemy():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(enemy_img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 3

    def update(self):
        if self.rect.x >= u9 * tile_size:
            self.diruection = -1
        elif self.rect.x <= 7 * tile_size:
            self.direction = 1
        self.rect.x += self.direction * self.speed
        screen.blit(self.image, self.rect)

    def reset(self):
        self.rect.x = 7 * tile_size
        self.rect.y = screen_height - tile_size * 4  # Two tiles up

# --- World Class ---
class World():
    def __init__(self, data):
        self.tile_list = []
        self.coins = []
        self.exit_rect = None
        dirt_img = pygame.image.load('dirt.png')
        dirt_img1 = pygame.image.load('dirt1.png')
        lava_img = pygame.image.load('lava.png')
        exit_img = pygame.image.load('exit.png')

        for row_idx, row in enumerate(data):
            for col_idx, tile in enumerate(row):
                x = col_idx * tile_size
                y = row_idx * tile_size
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                elif tile == 2:
                    img = pygame.transform.scale(lava_img, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                elif tile == 3:
                    img = pygame.transform.scale(dirt_img1, (tile_size, tile_size))
                    rect = img.get_rect(topleft=(x, y))
                    self.tile_list.append((img, rect))
                
                elif tile == 5:
                    img = pygame.transform.scale(exit_img, (tile_size + 20, tile_size * 2))
                    rect = img.get_rect(topleft=(x, y - 20))
                    self.tile_list.append((img, rect))
                    self.exit_rect = rect

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

# --- World Layout ---
world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 6, 0, 0, 0, 0],
    [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 2, 2, 2, 2],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
]

# --- Setup ---
world = World(world_data)
player = Player(100, screen_height - tile_size * 3)
enemy = Enemy(7 * tile_size, screen_height - tile_size * 4)

coins = [
    pygame.Rect(11 * tile_size, 2 * tile_size, tile_size, tile_size),
    pygame.Rect(11 * tile_size, 15 * tile_size, tile_size, tile_size),
    pygame.Rect(5 * tile_size, 4 * tile_size, tile_size, tile_size)
]

# --- Game Loop ---
run = True
game_over = False
win = False

while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))

    world.draw()
    for coin in coins:
        screen.blit(coin_img, coin)

    if not game_over and not win:
        player.update(world)
        enemy.update()
        player.check_collision(enemy)
        player.check_coins(coins)

        if player.health <= 0:
            game_over = True
        if player.check_exit(world.exit_rect):
            win = True
    else:
        font = pygame.font.SysFont(None, 60)
        if game_over:
            text = font.render("Game Over", True, (255, 0, 0))
        elif win:
            text = font.render("You Win!", True, (0, 255, 0))
        screen.blit(text, (screen_width // 2 - 100, screen_height // 2))

    # Health & Score UI
    for i in range(player.health):
        screen.blit(health_img, (i * 40 + 10, 10))
    font = pygame.font.SysFont(None, 40)
    score_text = font.render(f"Score: {player.score}", True, (255, 255, 0))
    screen.blit(score_text, (650, 10))

    # draw_grid()

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

    pygame.display.update()

pygame.quit()
