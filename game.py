# Имопрт библиотек
import pygame
import os
from GIFImage import GIFImage as gif
import time
from threading import Thread
import sqlite3

# Импортируем настройки
with open("config.txt") as config:
    settings = {
        i.split("=")[0].strip(): eval(i.split("=")[1])if i != '\n' and i[0] != '#' else None for i in config.readlines()
    }

# Задаём все необходимые константы
CHARACTER_SIZE = settings.get("CHARACTER_SIZE", (45, 75))
PLATFORM_SIZE = settings.get("PLATFORM_SIZE", (130, 17))
LADDER_SIZE = settings.get("LADDER_SIZE", (30, 100))
BARREL_SIZE = settings.get("BARREL_SIZE", (40, 40))
FALLING_SPEED = settings.get("FALLING_SPEED", 2)  # Скорость падения (pixels/tick)
BARREL_ROTATION = 3
LEFT, RIGHT = False, True  # Нужны для разворота персонажа направо/налево
BACKGROUND_COLOR = settings.get("BACKGROUND_COLOR", [255] * 3)
FPS = settings.get("FPS", 45)
JUMP_HEIGHT = settings.get("JUMP_HEIGHT", 100)
BARRELS_SPAWN_FREQUENCY = settings.get("BARRELS_SPAWN_FREQUENCY", 10)
WINDOW_SIZE = settings.get("WINDOW_SIZE", [(1000, 600), ])  # pygame.FULLSCREEN]
DEAD_HIGH = settings.get("DEAD_HIGH", 600)
JUMP_PER_TICK = settings.get("JUMP_PER_TICK", 15)


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


def get_map(lvl):
    con = sqlite3.connect("Map.db")
    cur = con.cursor()
    old_rec = cur.execute(
        """SELECT * FROM data WHERE id == ?""", (str(lvl),)).fetchone()
    con.close()
    return old_rec


class StartPos(pygame.sprite.Sprite):
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.transform.scale(load_image("start.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def move(self, x, y):
        self.rect.x, self.rect.y = x, y


class FinishPos(pygame.sprite.Sprite):
    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.transform.scale(load_image("finish.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, x, y):
        self.rect.x, self.rect.y = x, y


class Platform(pygame.sprite.Sprite):
    """Класс платформы. По ним персонаж будет ходить, а бочки катиться"""

    def __init__(self, group, pos):
        super().__init__(group)

        self.image = self.old_im = pygame.transform.scale(load_image("platform.png"), PLATFORM_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos
        self.angle = 0

    def get_center(self):
        return self.rect.x + self.rect.size[0] // 2, self.rect.y + self.rect.size[1] // 2

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

        self.image = self.old_im = pygame.transform.scale(load_image("barrel.png"), BARREL_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos
        self.boom = gif("images/boom.gif")
        self.speed = 0
        self.angle = 0
        self.reserve_impulse = 0

        super().__init__(group)

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

    def move(self, platforms, booms, barrels, enemy, is_gameover, screen, ladders, flags, x=0, y=0):

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
            Thread(target=gameover, args=[is_gameover, platforms, barrels, ladders, booms, flags, screen]).start()

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

    def update(self, platforms, booms, barrels, enemy, is_gameover, screen, ladders, flags):

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
            self.move(platforms, booms, barrels, enemy, is_gameover, ladders, screen, flags, x=delta)
        for _ in range(FALLING_SPEED):
            self.move(platforms, booms, barrels, enemy, is_gameover, ladders, screen, flags, y=1)

        super().update()


class Enemy(pygame.sprite.Sprite):
    """Класс персонажа, которым собственно и управляет игрок))"""

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

    def get_center(self):
        return self.rect.x + self.rect.size[0] // 2, self.rect.y + self.rect.size[1] // 2

    def move(self, platforms, ladders, barrels, booms, is_gameover, screen, flags, x=0, y=0):
        """Метод для передвижения персонажа. Передаётся перемещение по осям X и Y"""

        if x > 0:
            delta = 1
            self.step(RIGHT)
        elif x < 0:
            delta = -1
            self.step(LEFT)

        for _ in range(*sorted((x, 0))):
            self.rect = self.rect.move(delta, 0)
            stop = False

            ladds = pygame.sprite.spritecollide(self, ladders, dokill=False)
            for ladd in ladds:
                if pygame.sprite.collide_mask(self, ladd):
                    self.climbing = True
                    stop = True
                    break
            if stop:
                continue

            ss = pygame.sprite.spritecollide(self, platforms, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s):
                    self.rect = self.rect.move(0, -3)
                    ss2 = pygame.sprite.spritecollide(self, platforms, dokill=False)
                    for s2 in ss2:
                        if pygame.sprite.collide_mask(self, s):
                            self.rect = self.rect.move(0, 3)
                            break
                    else:
                        continue
                    self.rect = self.rect.move(-delta, 0)
                    stop = True
                    break
            if stop:
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

            if not self.climbing:
                ladds = pygame.sprite.spritecollide(self, ladders, dokill=False)
                for ladd in ladds:
                    if pygame.sprite.collide_mask(self, ladd):
                        self.climbing = True
                        stop = True
                        break
                if stop:
                    break

        ladds = pygame.sprite.spritecollide(self, ladders, dokill=False)
        for ladd in ladds:
            if pygame.sprite.collide_mask(self, ladd):
                self.climbing = True
                break
        else:
            self.climbing = False

        if not self.climbing:
            plt = pygame.sprite.spritecollide(self, platforms, dokill=False)
            for pl in plt:
                if pygame.sprite.collide_mask(self, pl):
                    if self.get_center()[1] > pl.get_center()[1] and pl.angle in (0, 180):
                        while pygame.sprite.collide_mask(self, pl) and not self.climbing:
                            self.rect.y += 1
                    else:
                        while pygame.sprite.collide_mask(self, pl) and not self.climbing:
                            self.rect.y -= 1

        bs = pygame.sprite.spritecollide(self, barrels, dokill=False)
        for b in bs:
            if pygame.sprite.collide_mask(self, b):
                t, *boom_info = b.booom()
                t.start()
                booms.append(boom_info)
                self.kill()
                Thread(
                    target=gameover,
                    args=[is_gameover, platforms, barrels, ladders, booms, flags, screen]
                ).start()

        if self.rect.y > DEAD_HIGH:
            self.kill()
            Thread(
                target=gameover,
                args=[is_gameover, platforms, barrels, ladders, booms, flags, screen]
            ).start()

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
        self.rect.x, self.rect.y = pos[0], pos[1] - CHARACTER_SIZE[1]


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


def gameover(is_gameover, platforms, barrels, ladders, booms, flags, screen):
    """Если мы проиграли, выводится соответствующее сообщение"""

    try:
        is_gameover[0] = True
        time.sleep(4)

        platforms.empty()
        barrels.empty()
        ladders.empty()
        flags.empty()
        booms.clear()
        screen.fill((0, 0, 0))

        myFont = pygame.font.SysFont("Comic Sans MS", 100)
        myText = myFont.render("Game Over", 1, (0, 255, 0))
        screen.blit(myText, (250, 200))
    except pygame.error:
        pass


def gg(is_gameover, platforms, barrels, ladders, booms, flags, screen, enemy, st_time, d_time):
    """Good Game - Well played"""

    d_time[0] = int(time.time() - st_time)

    is_gameover[0] = True

    platforms.empty()
    barrels.empty()
    ladders.empty()
    booms.clear()
    flags.empty()
    enemy.kill()

    screen.fill((0, 0, 0))
    myFont = pygame.font.SysFont("Comic Sans MS", 100)
    myText = myFont.render("Level Completed!", 1, (0, 255, 0))
    screen.blit(myText, (120, 200))


# База данных карт, вводится номер карты.
def bd(number):
    # преобразую базу данных
    dict_Plat = list()
    dict_Ladd = list()
    dict_Barrel = list()
    startpos = (0, 0)
    finishpos = (100, 100)

    con = sqlite3.connect('Map.db')
    cur = con.cursor()

    # Выводим данные из базы данных
    result = cur.execute("""SELECT * FROM data
              WHERE id == ?""", str(int(number)))

    for elem in result:

        for i in elem[1].split(';'):
            if not i:
                break
            dict_Plat.append(
                ((int(i.split(':')[0].split(',')[0]), int(i.split(':')[0].split(',')[1])), i.split(':')[1]))

        for i in elem[3].split(';'):
            if not i:
                break
            dict_Ladd.append((int(i.split(',')[0]), int(i.split(',')[1])))

        for i in elem[2].split(';'):
            if not i:
                break
            dict_Barrel.append((int(i.split(',')[0]), int(i.split(',')[1])))

        startpos = [int(i) for i in elem[4].split(",")]
        finishpos = [int(i) for i in elem[5].split(",")]

    # Когда разделим версии не забыть написать начальный ввод картинки!!!!!!!!!!!
    con.close()

    return dict_Plat, dict_Ladd, dict_Barrel, startpos, finishpos


def go(lvl):
    """Основная функция игрового цикла"""

    # Инициалтзация pygame программы
    pygame.init()

    screen = pygame.display.set_mode(*WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)

    # Создаём группы спрайтов
    platforms = pygame.sprite.Group()
    barrels = pygame.sprite.Group()
    ladders = pygame.sprite.Group()
    en = pygame.sprite.Group()
    flags = pygame.sprite.Group()

    # Подготавливаем программу к запуску игрового цикла
    platforms.draw(screen)
    clock = pygame.time.Clock()
    running = True
    booms = []
    is_gameover = [False]
    paused = False
    jump_impulse = 0

    # Засекаем время
    start_time = time.time()
    delta_time = [None]

    # Загружаем карту из БД
    map_ = bd(lvl)

    for i in map_[0]:
        p = Platform(platforms, i[0])
        p.rotate(int(i[1]))

    for i in map_[1]:
        Ladder(ladders, i)

    def spawn_barrels(poses, sprite_group, is_gameover):
        """С заданной частотой будет спавнить бочки"""

        while not is_gameover[0]:
            try:
                for pos in poses:
                    Barrel(sprite_group, pos)
            except pygame.error:
                break

            time.sleep(BARRELS_SPAWN_FREQUENCY)

    # Стартим поток спавна бочек
    Thread(target=spawn_barrels, args=[map_[2], barrels, is_gameover]).start()

    # Устанавливаем старт и финиш, спавним перса
    enemy = Enemy(en, map_[3])
    StartPos(flags, map_[3])
    finish = FinishPos(flags, map_[4])

    # Игровой цикл
    while running:

        # Костыль)))
        events = [pygame.event.EventType]
        events = pygame.event.get() + events
        events = events[:5]

        # Обрабатываем каждое событие циклом for
        for event in events:
            if event.type == pygame.QUIT:
                # Завершаем игровой цикл, если программу закрыли
                running = False
                break

            elif event.type == pygame.KEYDOWN and not is_gameover[0] and event.key == pygame.K_p:
                # Пауза
                paused = not paused
                continue

            elif event.type == pygame.MOUSEBUTTONDOWN and is_gameover[0]:
                # Выходим, если после конца игры нажали мышью
                running = False
                break

            elif enemy and not is_gameover[0]:
                # Если персонаж существует, проверяем, нужно ли его двигать

                if pygame.key.get_pressed()[pygame.K_LEFT]:
                    # Двигаем влево
                    enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, flags, x=-3)

                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    # Двигаем вправо
                    enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, flags, x=3)

                if pygame.key.get_pressed()[pygame.K_SPACE] and enemy.can_jump(platforms, ladders):
                    # Прыжок
                    jump_impulse = 5 if enemy.climbing else JUMP_HEIGHT

                if jump_impulse:
                    if jump_impulse >= JUMP_PER_TICK:
                        jump_impulse -= JUMP_PER_TICK
                        delta = JUMP_PER_TICK
                    else:
                        delta = jump_impulse
                        jump_impulse = 0

                    enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, flags, y=-delta)

                if enemy.climbing:
                    # Если герой на лестнице...

                    if pygame.key.get_pressed()[pygame.K_UP]:
                        # двигаем наверх
                        enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, flags, y=-3)

                    elif pygame.key.get_pressed()[pygame.K_DOWN]:
                        # двигаем вниз
                        enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, flags, y=3)

        if paused:
            pygame.time.wait(1000)
            continue

        if enemy and not enemy.climbing:
            # Если персонаж не на лестнице, на него действует гравитация
            enemy.move(platforms, ladders, barrels, booms, is_gameover, screen, flags, y=FALLING_SPEED)

        if not is_gameover[0]:
            screen.fill(BACKGROUND_COLOR)

            for bar in barrels:
                bar.update(platforms, booms, barrels, enemy, is_gameover, ladders, screen, flags)

        # Отрисовываем всё. что необходимо
        platforms.draw(screen)
        ladders.draw(screen)
        flags.draw(screen)

        # Воспроизводим анимацию взрывов
        for boom in booms:
            boom[0].render(screen, boom[1])

        if pygame.sprite.collide_mask(enemy, finish):
            gg(is_gameover, platforms, barrels, ladders,
               booms, flags, screen, enemy, start_time, delta_time)

        en.draw(screen)
        barrels.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

    return delta_time[0]


if __name__ == '__main__':
    go(6)
    pygame.quit()
