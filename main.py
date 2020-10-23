import pygame
import random

from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_a,
    K_s,
    K_d,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BASE_SPEED = 1
CURRENT_LEVEL = 1

#Custom Events:
ADDENEMY = pygame.USEREVENT + 1
SPEEDUP = pygame.USEREVENT + 2
ADDFUEL = pygame.USEREVENT + 3
UPDATEFUEL = pygame.USEREVENT + 4

pygame.time.set_timer(ADDENEMY, 1000)
pygame.time.set_timer(SPEEDUP, 10000)
pygame.time.set_timer(ADDFUEL, 3000)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((75, 25))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()

    def update(self, keys):
        if keys[K_UP] or keys[K_w]:
            self.rect.move_ip(0, -8)
        if keys[K_DOWN] or keys[K_s]:
            self.rect.move_ip(0, 8)
        if keys[K_LEFT] or keys[K_a]:
            self.rect.move_ip(-8, 0)
        if keys[K_RIGHT] or keys[K_d]:
            self.rect.move_ip(8, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_min):
        super().__init__()
        self.speed = random.randint(speed_min, speed_min+4)

        self.surf = pygame.image.load("asteroid.bmp").convert()
        self.surf = pygame.transform.scale(self.surf, (20,20))
        self.surf.set_colorkey((0,0,0), RLEACCEL)
        #self.surf = pygame.Surface((20, 10))
        #self.surf.fill((255, 120, 120))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    def speedup(self):
        self.speed += 1

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Fuel(pygame.sprite.Sprite):
    def __init__(self, speed_min):
        super().__init__()
        self.speed = random.randint(speed_min, speed_min + 4)

        self.surf = pygame.image.load("fuel0.bmp").convert()
        self.surf = pygame.transform.scale(self.surf, (25, 25))
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        #self.surf = pygame.Surface((20, 10))
        #self.surf.fill((120, 255, 120))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 25, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
    def speedup(self):
        self.speed += 1
    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class StatusText(pygame.sprite.Sprite):
    def __init__(self, label="", pad_from=(0,0)):
        super().__init__()
        self.rect = None
        self.surf = None
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.label = label + " {}"

        #ensure a left-sided padding of 10 units between StatusText sprites:
        self.upper_left = (pad_from[0]+10, pad_from[1])

        self.update(0)

    def update(self, num):
        text = self.label.format(num)
        self.surf = self.font.render(text, True, (255,255,255))
        self.rect = self.surf.get_rect(topleft=self.upper_left)


#################################
pygame.init()

#Blit Background Image From File:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_texture = pygame.image.load("bg_texture.bmp").convert()
bg_texture = pygame.transform.scale(bg_texture, (SCREEN_WIDTH, SCREEN_HEIGHT))
bg_texture.set_colorkey((0,0,0), RLEACCEL)
bg_rect = bg_texture.get_rect()

#Creating Non-repeating Sprites:
player = Player()
fuel_text = StatusText("Fuel:", (0,0))
health_text = StatusText("Health:", fuel_text.rect.topright)

#Crating Groups:
status_objs = pygame.sprite.Group()
enemies = pygame.sprite.Group()
friends = pygame.sprite.Group()
moving_objs = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

#Adding to Groups:
status_objs.add(fuel_text)
status_objs.add(health_text)

all_sprites.add(fuel_text)
all_sprites.add(health_text)
all_sprites.add(player)

# Event Loop:
clock = pygame.time.Clock()

speed_addend = 0
fuel_count = 0
player_HP = 15

running = True
while running:
    health_text.update(player_HP)
    screen.fill((0, 0, 0))
    screen.blit(bg_texture, bg_rect)

    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        elif event.type == QUIT:
            running = False

        elif fuel_count == 20:
            "Success!"
            running = False

        elif event.type == UPDATEFUEL:
            fuel_text.update(fuel_count)

        elif event.type == ADDENEMY:
            speed = (BASE_SPEED * CURRENT_LEVEL) + speed_addend
            new_enemy = Enemy(speed)
            enemies.add(new_enemy)
            moving_objs.add(new_enemy)
            all_sprites.add(new_enemy)

        elif event.type == ADDFUEL:
            speed = (BASE_SPEED * CURRENT_LEVEL) + speed_addend
            new_fuel = Fuel(speed)
            friends.add(new_fuel)
            moving_objs.add(new_fuel)
            all_sprites.add(new_fuel)
            print("New Fuel")

        elif event.type == SPEEDUP:
            for sprite in moving_objs:
                sprite.speedup()

            speed_addend += 1
            print("SPEEDUP")

    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)
    moving_objs.update()

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    if pygame.sprite.spritecollide(player, friends, True):
        fuel_count += 1
        fuel_text.update(fuel_count)
        print("Fuel: {}".format(fuel_count))

    if pygame.sprite.spritecollide(player, enemies, True):
        player_HP -= 5
        health_text.update(player_HP)
        if player_HP <= 0:
            player.kill()
            running = False
            print("You Died.")
        print("Health: {}".format(player_HP))


    pygame.display.flip()

    clock.tick(60)