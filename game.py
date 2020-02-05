# Имопрт библиотек
import pygame
import os
from GIFImage import GIFImage as gif
import time
from threading import Thread

# Задаём все необходимые константы
CHARACTER_SIZE = 60, 100
PLATFORM_SIZE = 150, 25
LADDER_SIZE = 50, 120
BARREL_SIZE = 30, 30
FALLING_SPEED = 2  # Скорость падения (pixels/tick)
BARREL_ROTATION = 3
WINDOW_SIZE = 1000, 600
LEFT, RIGHT = False, True  # Нужны для разворота персонажа направо/налево
BACKGROUND_COLOR = [255] * 3
FPS = 60
JUMP_HEIGHT = 80


def load_image(name, colorkey=None):
    """Функция для открытия изображения в pygame.image"""

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


class Platform(pygame.sprite.Sprite):
    """Класс платформы. По ним персонаж будет ходить, а бочки катиться"""

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = self.old_im = pygame.transform.scale(load_image("platform.png"), PLATFORM_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos
        self.angle = 0

    def rotate(self, angle):
        """Метод поворота (наклона) платформы (платформа вращается вокруг центра. Передаётся угол"""

        self.angle += angle
        self.angle %= 360

        self.image = pygame.transform.rotate(self.old_im, self.angle)

        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.x = center[0] - self.rect.center[0]
        self.rect.y = center[1] - self.rect.center[1]

        self.mask = pygame.mask.from_surface(self.image)


class Ladder(pygame.sprite.Sprite):
    """Класс лестницы. По ним персонаж будет лазить"""

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.transform.scale(load_image("ladder.png"), LADDER_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos


class Barrel(pygame.sprite.Sprite):
    """Класс бочки. Она катится по платформам и взрывается при контакте с ней персонажа"""

    def __init__(self, group, pos):
        super().__init__(group)

        self.image = self.old_im = pygame.transform.scale(load_image("barrel.png"), BARREL_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos
        self.boom = gif("images/boom.gif")
        self.speed = 0
        self.angle = 0
        self.reserve_impulse = 0

    def get_center(self):
        """Получаем координаты центра бочки"""
        return self.rect.x + self.rect.size[0] // 2, self.rect.y + self.rect.size[1] // 2

    def booom(self):
        """Метод, взрывающий бочку (запускает поток, который вовремя остановит анимацию взрыва)"""

        self.kill()

        def for_thread(boom):
            time.sleep(9)
            boom.pause()

        cent = self.get_center()
        return Thread(target=for_thread, args=(self.boom,)), self.boom, (cent[0] - 55, cent[1] - 60)

    def move(self, platforms, booms, barrels, enemy, is_gameover, screen, ladders, x=0, y=0):

        self.rect = self.rect.move(x, 0)
        ss = pygame.sprite.spritecollide(self, platforms, dokill=False)
        for s in ss:
            if pygame.sprite.collide_mask(self, s):
                self.rect = self.rect.move(-x, 0)
                break

        self.rect = self.rect.move(0, y)
        ss = pygame.sprite.spritecollide(self, platforms, dokill=False)
        for s in ss:
            if pygame.sprite.collide_mask(self, s):
                self.rect = self.rect.move(0, -y)
                break

        bs = pygame.sprite.spritecollide(self, barrels, dokill=False)
        for b in bs:
            if pygame.sprite.collide_mask(self, b) and self != b:
                t, *boom_info = b.booom()
                t.start()
                booms.append(boom_info)

                t, *boom_info = self.booom()
                t.start()
                booms.append(boom_info)

        if enemy and pygame.sprite.collide_mask(self, enemy):
            t, *boom_info = self.booom()
            t.start()
            booms.append(boom_info)
            enemy.kill()
            Thread(target=gameover, args=[is_gameover, platforms, barrels, ladders, booms, screen]).start()

    def speed_update(self, platforms):
        """Изменяем скорость бочки в зависимости от положения платформы под ней"""

        self.rect = self.rect.move(0, 1)

        ps = pygame.sprite.spritecollide(self, platforms, dokill=False)
        for p in ps:
            if pygame.sprite.collide_mask(self, p):
                if p.angle // 90 % 2:
                    self.speed = 1
                    self.reserve_impulse = 160
                elif p.angle != 0:
                    self.speed = -1
                    self.reserve_impulse = 160
                else:
                    if self.reserve_impulse == 0:
                        self.speed = 0
                    self.reserve_impulse -= 1

        self.rect = self.rect.move(0, -1)

    def update(self, platforms, booms, barrels, enemy, is_gameover, screen, ladders):

        self.speed_update(platforms)

        if self.speed < 0:
            self.angle += BARREL_ROTATION
        elif self.speed > 0:
            self.angle -= BARREL_ROTATION

        self.angle %= 360

        x, y = self.rect.x, self.rect.y
        self.image = pygame.transform.rotate(self.old_im, self.angle)
        self.rect = self.image.get_rect()
        s = self.rect.size
        xx, yy = (s[0] - BARREL_SIZE[0]) // 2, (s[1] - BARREL_SIZE[1]) // 2
        self.image = pygame.transform.chop(self.image, (0, 0, xx, yy))
        self.image = pygame.transform.chop(self.image, (*BARREL_SIZE, xx, yy))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

        delta = 1 if self.speed > 0 else -1
        for _ in range(*sorted((self.speed, 0))):
            self.move(platforms, booms, barrels, enemy, is_gameover, ladders, screen, x=delta)
        for _ in range(FALLING_SPEED):
            self.move(platforms, booms, barrels, enemy, is_gameover, ladders, screen, y=1)

        super().update()


class Enemy(pygame.sprite.Sprite):
    """Класс персонажа, которым собственно и управляет игрок))"""

    # Подгружаем 2 состояния персонажа (с разным положением ног для имитации шагов)
    # image1 = load_image("character_1.png")
    # image2 = load_image("character_2.png")

    def __init__(self, group, pos):
        super().__init__(group)
        self.image1 = load_image("skin_1_1.png")
        self.image2 = load_image("skin_1_2.png")
        self.active_step = 0
        self.rotation = RIGHT
        self.image = pygame.transform.scale(self.image1, CHARACTER_SIZE)
        self.rect = self.image.get_rect()
        self.climbing = False
        self.mask = pygame.mask.from_surface(self.image)
        self.spawn(pos)

    def move(self, platforms, ladders, barrels, booms, is_gameover, screen, x=0, y=0):
        """Метод для передвижения персонажа. Передаётся перемещение по осям X и Y"""

        if x > 0:
            delta = 1
            self.step(RIGHT)
        elif x < 0:
            delta = -1
            self.step(LEFT)

        for _ in range(*sorted((x, 0))):
            self.rect = self.rect.move(delta, 0)

            ss = pygame.sprite.spritecollide(self, platforms, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s):
                    self.rect = self.rect.move(-delta, 0)
                    break

        delta = 1 if y > 0 else -1
        stop = False
        for _ in range(*sorted((y, 0))):
            self.rect = self.rect.move(0, delta)

            if not self.climbing:
                ss = pygame.sprite.spritecollide(self, platforms, dokill=False)
                for s in ss:
                    if pygame.sprite.collide_mask(self, s):
                        self.rect = self.rect.move(0, -delta)
                        stop = True
                        break
                if stop:
                    break

            ss = pygame.sprite.spritecollide(self, ladders, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s):
                    if not self.climbing:
                        stop = True
                    break
            else:
                self.climbing = False
            if stop:
                break

        ss = pygame.sprite.spritecollide(self, ladders, dokill=False)
        for s in ss:
            if pygame.sprite.collide_mask(self, s):
                self.climbing = True
                break
        else:
            self.climbing = False

        bs = pygame.sprite.spritecollide(self, barrels, dokill=False)
        for b in bs:
            if pygame.sprite.collide_mask(self, b):
                t, *boom_info = b.booom()
                t.start()
                booms.append(boom_info)
                self.kill()
                Thread(target=gameover, args=[is_gameover, platforms, barrels, ladders, booms, screen]).start()

    def can_jump(self, platforms, ladders):
        """Проверка, есть ли от чего оттолкнуться для прыжка"""

        self.rect = self.rect.move(0, 1)

        r = True
        res = pygame.sprite.spritecollide(self, platforms, dokill=False) + \
              pygame.sprite.spritecollide(self, ladders, dokill=False)

        for s in res:
            if pygame.sprite.collide_mask(self, s):
                break
        else:
            r = False

        self.rect = self.rect.move(0, -1)

        return r

    def step(self, direction):
        """Шаг персонажа, т.е. смена его картинки"""

        self.active_step += 1
        self.image = eval(f"pygame.transform.scale(self.image{self.active_step // 8 % 2 + 1}, CHARACTER_SIZE)")
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

    def spawn(self, pos):
        self.rect.x, self.rect.y = [i[0] - i[1] // 2 for i in zip(pos, CHARACTER_SIZE)]


class Nothing(pygame.sprite.Sprite):
    """Класс используемый для тестирования всяких штук"""

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.rect = pygame.Rect(*pos, 5, 5)

    def choose_platform(self, platforms):
        return pygame.sprite.spritecollideany(self, platforms)

    def choose_ladder(self, ladders):
        return pygame.sprite.spritecollideany(self, ladders)


def gameover(is_gameover, platforms, barrels, ladders, booms, screen):
    """Если мы проиграли, выводится соответствующее сообщение"""

    is_gameover[0] = True
    time.sleep(6)

    platforms.empty()
    barrels.empty()
    ladders.empty()
    booms.clear()
    screen.fill((0, 0, 0))

    myFont = pygame.font.SysFont("Comic Sans MS", 100)
    myText = myFont.render("Game Over", 1, (0, 255, 0))
    screen.blit(myText, (250, 200))


def main():
    # Инициалтзация pygame программы
    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)

    # Создаём группы спрайтов
    platforms = pygame.sprite.Group()
    barrels = pygame.sprite.Group()
    ladders = pygame.sprite.Group()
    en = pygame.sprite.Group()

    # Подготавливаем программу к запуску игрового цикла
    platforms.draw(screen)
    enemy = None
    clock = pygame.time.Clock()
    running = True
    booms = []
    is_gameover = [False]

    # Игровой цикл
    while running:
        # Обрабатываем каждое событие циклом for
        events = [pygame.event.EventType]
        events = pygame.event.get() + events
        events = events[:5]
        for event in events:
            if event.type == pygame.QUIT:
                # Завершаем игровой цикл, если программу закрыли
                running = False

            elif event.type == pygame.KEYDOWN and not is_gameover[0]:
                platform = Nothing(pygame.mouse.get_pos()).choose_platform(platforms)
                # Пока ALT и DEL будут служебными клавишами для всяких тестируемх штук
                if platform:
                    if event.key == pygame.K_LALT:
                        # По нажатию ALT разворачивается платформа, на которую наведена мышь
                        platform.rotate(30)
                    elif event.key == pygame.K_DELETE:
                        platform.kill()

            elif event.type == pygame.MOUSEBUTTONDOWN and not is_gameover[0]:
                # Обработка событий кликов мышкой

                if event.button == 1:
                    # Если клик левой кнопкой, рисуем...
                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        # лестницу, если зажата клавиша левый Ctrl
                        Ladder(ladders, event.pos)
                    else:
                        # платформу
                        Platform(platforms, event.pos)

                elif event.button == 3:
                    # если правая кнопка мыши, помещаем персонажа в координаты нажатия
                    if enemy:
                        enemy.spawn(event.pos)
                    else:
                        enemy = Enemy(en, event.pos)

                elif event.button == 2:
                    # По нажатию на колёсико мыши создаётся бочка
                    if barrels and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        # Если зажата клафиша CTRL, то бочка, на которой находится курсор, взрывается
                        b = pygame.sprite.spritecollideany(Nothing(event.pos), barrels)
                        if b:
                            t, *boom_info = b.booom()
                            t.start()
                            booms.append(boom_info)

                    else:
                        b = Barrel(barrels, event.pos)

            elif enemy and not is_gameover[0]:
                # Если персонаж существует, проверяем, нужно ли его двигать

                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    # Двигаем влево
                    enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, x=-3)

                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    # Двигаем вправо
                    enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, x=3)

                if pygame.key.get_pressed()[pygame.K_SPACE] and enemy.can_jump(platforms, ladders):
                    # Прыжок
                    delta = 5 if enemy.climbing else JUMP_HEIGHT
                    enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, y=-delta)

                if enemy.climbing:
                    # Если герой на лестнице...

                    if pygame.key.get_pressed()[pygame.K_UP]:
                        # двигаем наверх
                        enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, y=-3)

                    elif pygame.key.get_pressed()[pygame.K_DOWN]:
                        # двигаем вниз
                        enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, y=3)

        if enemy and not enemy.climbing:
            # Если персонаж не на лестнице, на него действует гравитация
            enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, y=FALLING_SPEED)

        if not is_gameover[0]:
            screen.fill(BACKGROUND_COLOR)

        # Отрисовываем всё. что необходимо
        platforms.draw(screen)
        ladders.draw(screen)

        # Воспроизводим анимацию взрывов
        for boom in booms:
            boom[0].render(screen, boom[1])

        for bar in barrels:
            bar.update(platforms, booms, barrels, enemy, is_gameover, ladders, screen)

        en.draw(screen)
        barrels.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    # Выходим из pygame по завершении игрового цикла
    pygame.quit()


if __name__ == '__main__':
    main()
