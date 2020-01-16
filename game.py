import pygame

CHARACTER_SIZE = 30, 30
FALLING_SPEED = 2  # Скорость падения (pixels/tick)

pygame.init()

size = width, height = 1000, 600

screen = pygame.display.set_mode(size)
running = True

platforms = pygame.sprite.Group()
barrels = pygame.sprite.Group()
ladders = pygame.sprite.Group()


class Platform(pygame.sprite.Sprite):
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.Surface((50, 10))
        pygame.draw.rect(self.image, (128, 128, 128), (0, 0, 50, 10))
        self.rect = pygame.Rect(*pos, 50, 10)


class Ladder(pygame.sprite.Sprite):
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.Surface((10, 50))
        pygame.draw.rect(self.image, (254, 0, 0), (0, 0, 10, 50))
        self.rect = pygame.Rect(*pos, 10, 50)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.Surface(CHARACTER_SIZE)
        pygame.draw.rect(self.image, (0, 0, 255), (0, 0, *CHARACTER_SIZE))
        self.rect = pygame.Rect(*pos, *CHARACTER_SIZE)
        self.climbing = False

    def move(self, x=0, y=0):

        delta = 1 if x > 0 else -1
        for _ in range(*sorted((x, 0))):
            self.rect = self.rect.move(delta, 0)
            if pygame.sprite.spritecollideany(self, platforms):
                self.rect = self.rect.move(-delta, 0)
                break
            if pygame.sprite.spritecollideany(self, barrels):
                return True

        delta = 1 if y > 0 else -1
        for _ in range(*sorted((y, 0))):
            self.rect = self.rect.move(0, delta)
            if pygame.sprite.spritecollideany(self, platforms) and not self.climbing:
                self.rect = self.rect.move(0, -delta)
                break
            if pygame.sprite.spritecollideany(self, barrels):
                return True
            if pygame.sprite.spritecollideany(self, ladders) and not self.climbing:
                self.climbing = True
                break

        if pygame.sprite.spritecollideany(self, ladders):
            self.climbing = True
        else:
            self.climbing = False

    def can_jump(self):
        """Проверка, есть ли от чего оттолкнуться для прыжка"""

        self.rect = self.rect.move(0, 1)

        res = bool(pygame.sprite.spritecollideany(self, platforms) or
                   pygame.sprite.spritecollideany(self, ladders))
        self.rect = self.rect.move(0, -1)
        return res


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
