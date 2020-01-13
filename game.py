import pygame

CHARACTER_SIZE = 30, 30
G = 0  # Ускорение свободного падения (pix/tick)

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
        self.speed = [0, 0]  # Перемещение по X и Y за tick

    def move(self):
        print(self.speed)
        for x in range(*sorted((self.speed[0], 0))):
            if not pygame.sprite.spritecollideany(self, platforms):
                self.rect = self.rect.move(1, 0) if x > 0 else self.rect.move(-1, 0)
            else:
                break

        for y in range(*sorted((self.speed[1], 0))):
            if not (pygame.sprite.spritecollideany(self, platforms) or
                    pygame.sprite.spritecollideany(self, ladders)):
                self.rect = self.rect.move(0, 1) if y > 0 else self.rect.move(0, -1)
            else:
                break

        self.speed[1] += G

        if pygame.sprite.spritecollideany(self, ladders):
            self.climbing = True

    def can_jump(self):
        self.rect = self.rect.move(0, 1)
        yield pygame.sprite.spritecollideany(self, platforms) or\
            pygame.sprite.spritecollideany(self, ladders)

        self.rect = self.rect.move(0, -1)


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
                enemy.speed[0] -= 10
                enemy.move()
                enemy.speed[0] += 10
            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                enemy.speed[0] += 10
                enemy.move()
                enemy.speed[0] -= 10
            elif pygame.key.get_pressed()[pygame.K_SPACE] and enemy.can_jump():
                enemy.speed[1] -= 30
                enemy.move()
                enemy.speed[1] += 30
            elif enemy.climbing:
                if pygame.key.get_pressed()[pygame.K_UP]:
                    enemy.speed[1] -= 10
                    enemy.move()
                    enemy.speed[1] += 10
                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    enemy.speed[1] += 10
                    enemy.move()
                    enemy.speed[1] -= 10

    if enemy: enemy.move()
    screen.fill((255, 255, 255))
    platforms.draw(screen)
    ladders.draw(screen)
    en.draw(screen)
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
