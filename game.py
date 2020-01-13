import pygame

pygame.init()

size = width, height = 500, 500

screen = pygame.display.set_mode(size)
running = True

platforms = pygame.sprite.Group()
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
        self.image = pygame.Surface((20, 20))
        pygame.draw.rect(self.image, (0, 0, 255), (0, 0, 20, 20))
        self.rect = pygame.Rect(*pos, 20, 20)
        self.climbing = False

    def move(self, x, y, falling=False):
        self.rect = self.rect.move(x, y)
        q = pygame.sprite.spritecollideany(self, platforms)
        if q and falling:
            self.rect = self.rect.move(0, -y)
        if pygame.sprite.spritecollideany(self, ladders):
            self.climbing = True
        else:
            self.climbing = False


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
        elif event.type == pygame.KEYDOWN:
            if enemy:
                if event.key == 275:
                    enemy.move(10, 0)
                elif event.key == 276:
                    enemy.move(-10, 0)
                elif enemy.climbing:
                    if event.key == 274:
                        enemy.move(0, 10)
                    elif event.key == 273:
                        enemy.move(0, -10)

    if enemy and not enemy.climbing:
        enemy.move(0, 1, falling=True)

    screen.fill((255, 255, 255))
    platforms.draw(screen)
    ladders.draw(screen)
    en.draw(screen)
    pygame.display.flip()
    clock.tick(50)

pygame.quit()