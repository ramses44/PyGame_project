import pygame
import os

CHARACTER_SIZE = 60, 100
PLATFORM_SIZE = 150, 25
LADDER_SIZE = 50, 120
FALLING_SPEED = 2  # Скорость падения (pixels/tick)
LEFT, RIGHT = False, True


def load_image(name, colorkey=None):
    fullname = os.path.join('images', name)
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
        image.set_alpha(0)

    return image


pygame.init()

size = width, height = 1000, 600

screen = pygame.display.set_mode(size)
running = True

platforms = pygame.sprite.Group()
barrels = pygame.sprite.Group()
ladders = pygame.sprite.Group()


class Platform(pygame.sprite.Sprite):
    image = load_image("platform.png")

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.transform.scale(Platform.image, PLATFORM_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos


class Ladder(pygame.sprite.Sprite):
    image = load_image("ladder.png")

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.transform.scale(Ladder.image, LADDER_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos


class Enemy(pygame.sprite.Sprite):
    image1 = load_image("character_1.png")
    image2 = load_image("character_2.png")

    def __init__(self, group, pos):
        super().__init__(group)
        self.active_step = 0
        self.rotation = RIGHT
        self.image = pygame.transform.scale(Enemy.image1, CHARACTER_SIZE)
        self.rect = self.image.get_rect()
        self.climbing = False
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos

    def move(self, x=0, y=0):

        if x > 0:
            delta = 1
            self.step(RIGHT)
        elif x < 0:
            delta = -1
            self.step(LEFT)

        for _ in range(*sorted((x, 0))):
            self.rect = self.rect.move(delta, 0)

            s = pygame.sprite.spritecollideany(self, platforms)
            if s and pygame.sprite.collide_mask(self, s):
                self.rect = self.rect.move(-delta, 0)
                break

            s = pygame.sprite.spritecollideany(self, barrels)
            if s and pygame.sprite.collide_mask(self, s):
                return True

        delta = 1 if y > 0 else -1
        for _ in range(*sorted((y, 0))):
            self.rect = self.rect.move(0, delta)

            s = pygame.sprite.spritecollideany(self, platforms)
            if s and pygame.sprite.collide_mask(self, s):
                self.rect = self.rect.move(0, -delta)
                break

            s = pygame.sprite.spritecollideany(self, barrels)
            if s and pygame.sprite.collide_mask(self, s):
                return True

            s = pygame.sprite.spritecollideany(self, ladders)
            if s and pygame.sprite.collide_mask(self, s) and not self.climbing:
                self.climbing = True
                break

        s = pygame.sprite.spritecollideany(self, ladders)
        if s and pygame.sprite.collide_mask(self, s):
            self.climbing = True
        else:
            self.climbing = False

    def can_jump(self):
        """Проверка, есть ли от чего оттолкнуться для прыжка"""

        self.rect = self.rect.move(0, 1)

        res = pygame.sprite.spritecollideany(self, platforms)
        if not res:
            res = pygame.sprite.spritecollideany(self, ladders)
        res = bool(res and pygame.sprite.collide_mask(self, res))

        self.rect = self.rect.move(0, -1)
        return res

    def step(self, direction):
        """Шаг персонажа, т.е. смена его картинки"""

        self.image = eval(f"pygame.transform.scale(Enemy.image{self.active_step + 1}, CHARACTER_SIZE)")
        self.active_step = (self.active_step + 1) % 2
        self.rotation = RIGHT

        x, y = self.rect.x, self.rect.y
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        self.rotate(direction)

    def rotate(self, direction):
        """Поворот персонажа на 180 градусов"""

        if self.rotation != direction:
            self.rotation = direction
            self.image = pygame.transform.flip(self.image, True, False)

            x, y = self.rect.x, self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = x, y


screen.fill((255, 255, 255))
platforms.draw(screen)
enemy = None
clock = pygame.time.Clock()
en = pygame.sprite.Group()

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if pygame.key.get_pressed()[305] or pygame.key.get_pressed()[306]:
                    Ladder(ladders, event.pos)
                else:
                    Platform(platforms, event.pos)
            elif event.button == 3:
                if enemy:
                    enemy.rect.x, enemy.rect.y = event.pos
                else:
                    enemy = Enemy(en, event.pos)
        if enemy:
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                enemy.move(x=-10)

            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                enemy.move(x=10)

            elif pygame.key.get_pressed()[pygame.K_SPACE] and enemy.can_jump():
                enemy.move(y=-60)
            elif enemy.climbing:
                if pygame.key.get_pressed()[pygame.K_UP]:
                    enemy.move(y=-10)
                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    enemy.move(y=10)

    if enemy and not enemy.climbing: enemy.move(y=FALLING_SPEED)
    screen.fill((255, 255, 255))
    platforms.draw(screen)
    ladders.draw(screen)
    en.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
