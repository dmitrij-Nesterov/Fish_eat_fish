import pygame as pg
from pygame.constants import *
import os
from random import randint
pg.init()
pg.mixer.init()

class Fish:
    def __init__(self, name):
        self.original_image = pg.image.load(f'images/{name}.png')
        self.image = self.original_image.copy()
        self.procesing_image()

    def procesing_image(self, in_less = 20, is_flip = False):
        self.image = pg.transform.scale(self.original_image, (self.original_image.get_width() // in_less // (1360 / WIDTH), \
                                                             self.original_image.get_height() // in_less // (720 / HEIGHT)))
        self.image = pg.transform.flip(self.image, flip_x = is_flip, flip_y = False)
        self.image.set_colorkey((255, 255, 255))
        self.image = self.image.convert_alpha(screen)

class FishNPC(Fish, pg.sprite.Sprite):
    SPEED = 2
    def __init__(self, group):
        pg.sprite.Sprite.__init__(self)
        Fish.__init__(self, fish_NPC_names[randint(0, len(fish_NPC_names)-1)])

        player = fish_players_group.sprites()[randint(0, len(fish_players_group)-1)]
        player_score_index = size_division_fish[player.score]
        self.score = size_division_fish[randint(max(0, player_score_index - 2), min(len(size_division_fish)-1, player_score_index + 2))]
        self.procesing_image(in_less = 20-size_division_fish.index(self.score))

        self.is_flip = randint(0, 1)
        self.rect = self.image.get_rect(top = randint(0, HEIGHT - self.image.get_height()), \
                                        left = self.is_flip * (WIDTH - 2) + 1)
        self.add(group)
        if self.is_flip:
            self.procesing_image(is_flip = True)

    def update(self):
        if self.rect.colliderect(screen.get_rect()):
            if self.is_flip:
                self.rect.move_ip(-self.SPEED, 0)
            else:
                self.rect.move_ip(self.SPEED, 0)
        else:
            self.kill()

class FishPlayer(Fish, pg.sprite.Sprite):
    SPEED = 4
    def __init__(self, group, left = K_LEFT, right = K_RIGHT, up = K_UP, down = K_DOWN):
        Fish.__init__(self, 'player')
        pg.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect(center = (WIDTH // 2, HEIGHT // 2))
        self.is_flip_fish = False #Повернута ли рыбка в лево
        self.flip_fish = False #Надо ли повернуть рыбку в лево
        self.add(group)
        self.score = 0
        self.id = fish_players_group.sprites().index(self)

        self.left = left
        self.right = right
        self.up = up
        self.down = down

    def update(self):
        text_score = font.render(f'Игрок {self.id + 1}: {self.score}', True, (255, 0, 0))
        screen.blit(text_score, (0, self.id * (WIDTH - text_score.get_width())))

        keys_pressed = pg.key.get_pressed()
        if keys_pressed[self.right] and screen.get_rect().contains(self.rect.move(self.SPEED, 0)):
            self.rect.move_ip(self.SPEED, 0)
            self.flip_fish = False
        elif keys_pressed[self.left] and screen.get_rect().contains(self.rect.move(-self.SPEED, 0)):
            self.rect.move_ip(-self.SPEED, 0)
            self.flip_fish = True

        if keys_pressed[self.down] and screen.get_rect().contains(self.rect.move(0, self.SPEED)):
            self.rect.move_ip(0, self.SPEED)
        elif keys_pressed[self.up] and screen.get_rect().contains(self.rect.move(0, -self.SPEED)):
            self.rect.move_ip(0, -self.SPEED)

        if self.is_flip_fish != self.flip_fish:
            self.procesing_image(is_flip = self.flip_fish)
            self.is_flip_fish = not self.is_flip_fish

        self.eat()

    def eat(self):
        hits = pg.sprite.spritecollide(self, fishs_NPC_group, False)
        for hit in hits:
            if self.score >= hit.score:
                if hit.score > 0:
                    self.score += hit.score // 4
                else:
                    self.score += 10
                hit.kill()
            else:
                self.kill()


FPS = 60
WIDTH = pg.display.Info().current_w
HEIGHT = pg.display.Info().current_h

pg.mixer.music.load('sounds/music.mp3')
pg.mixer.music.play(-1)
eat_sound = pg.mixer.Sound('sounds/eat_sound.ogg')

backgorund = pg.transform.scale(pg.image.load('images/background.jpg'), (WIDTH, HEIGHT))
font = pg.font.Font(None, 36)

screen = pg.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
clock = pg.time.Clock()

fish_NPC_names = ['barbus', 'fish-butterfly', 'orange', 'tadpole']
fishs_NPC_group = pg.sprite.Group()
fish_players_group = pg.sprite.Group()
FishPlayer(fish_players_group, left = K_LEFT, right = K_RIGHT, up = K_UP, down = K_DOWN)
FishPlayer(fish_players_group, left = K_a, right = K_d, up = K_w, down = K_s)

size_division_fish = []
size_fish = 0
while len(size_division_fish) < 20:
    if size_fish >= 100:
        size_division_fish.append(size_fish)
        size_fish *= 2
        size_division_fish.append(size_fish)
        size_fish *= 5
    else:
        size_division_fish.append(size_fish)
        size_fish = 100
        size_division_fish.append(size_fish)
        size_fish *= 5

NEW_FISH = USEREVENT
pg.time.set_timer(NEW_FISH, 2000)
while True:
    clock.tick(FPS)
    screen.blit(backgorund, (0, 0))

    if len(fish_players_group) == 0:
        quit()

    fishs_NPC_group.update()
    fish_players_group.update()

    for event in pg.event.get():
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                quit()
        if event.type == NEW_FISH:
            FishNPC(fishs_NPC_group)

    fishs_NPC_group.draw(screen)
    fish_players_group.draw(screen)
    pg.display.update()