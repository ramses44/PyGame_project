"""Никому н@х*й не нужная программа (типо игра)"""

# Имопрт библиотек
import pygame
import os

# Задаём все необходимые константы
CHARACTER_SIZE = 60, 100
PLATFORM_SIZE = 150, 25
LADDER_SIZE = 50, 120
FALLING_SPEED = 2  # Скорость падения (pixels/tick)
WINDOW_SIZE = 600, 400
LEFT, RIGHT = False, True  # Нужны для разворота персонажа направо/налево
BACKGROUND_COLOR = (228, 228, 228)
FPS = 60

# Инициалтзация pygame программы
pygame.init()

screen = pygame.display.set_mode(WINDOW_SIZE)
screen.fill(BACKGROUND_COLOR)


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
    """Класс платформы. По ним персонаж будет ходить, а бочки катиться"""  # или не будут))

    image = load_image("platform.png")  # Загружаем изображение платформы из файла

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = self.old_im = pygame.transform.scale(Platform.image, PLATFORM_SIZE)
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

    image = load_image("ladder.png")

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = pygame.transform.scale(Ladder.image, LADDER_SIZE)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos


class Enemy(pygame.sprite.Sprite):
    """Класс персонажа, которым собственно и управляет игрок))"""

    # Подгружаем 2 состояния персонажа (с разным положением ног для имитации шагов)
    # Сейчас перс представлен мужиком с большой головой и сигаретой)
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
        self.spawn(pos)

    def move(self, x=0, y=0):
        """Метод для передвижения персонажа.
        передаётся перемещение по осям X и Y"""  # можно поменять последние 3 буквы местами...))

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

            ss = pygame.sprite.spritecollide(self, barrels, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s):
                    return True

        delta = 1 if y > 0 else -1
        stop = False
        for _ in range(*sorted((y, 0))):
            self.rect = self.rect.move(0, delta)

            ss = pygame.sprite.spritecollide(self, platforms, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s):
                    self.rect = self.rect.move(0, -delta)
                    stop = True
                    break
            if stop:
                break

            ss = pygame.sprite.spritecollide(self, barrels, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s):
                    return True

            ss = pygame.sprite.spritecollide(self, ladders, dokill=False)
            for s in ss:
                if pygame.sprite.collide_mask(self, s) and not self.climbing:
                    stop = True
                    break
            if stop:
                break

        ss = pygame.sprite.spritecollide(self, ladders, dokill=False)
        for s in ss:
            if pygame.sprite.collide_mask(self, s) and not self.climbing:
                self.climbing = True
                break
            else:
                self.climbing = False

    def can_jump(self):
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

    def spawn(self, pos):
        self.rect.x, self.rect.y = [i[0] - i[1] // 2 for i in zip(pos, CHARACTER_SIZE)]


class Nothing(pygame.sprite.Sprite):
    """Класс используемый для тестирования всяких штук"""

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.rect = pygame.Rect(*pos, 5, 5)

    def choose_platform(self):
        return pygame.sprite.spritecollideany(self, platforms)

    def choose_ladder(self):
        return pygame.sprite.spritecollideany(self, ladders)


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

# Игровой цикл
while running:
    # Обрабатываем каждое событие циклом for
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Завершаем игровой цикл, если программу закрыли
            running = False

        elif pygame.key.get_pressed()[pygame.K_LALT]:
            # Пока ALT будет служебной клавишей для всяких тестируемх штук

            # По нажатию ALT разворачивается платформа, на которую наведена мышь
            platform = Nothing(pygame.mouse.get_pos()).choose_platform()
            if platform:
                platform.rotate(60)

        elif event.type == pygame.MOUSEBUTTONDOWN:
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

        elif enemy:
            # Если персонаж существует, проверяем, нужно ли его двигать

            if pygame.key.get_pressed()[pygame.K_LEFT]:
                # Двигаем влево
                enemy.move(x=-10)

            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                # Двигаем вправо
                enemy.move(x=10)

            elif pygame.key.get_pressed()[pygame.K_SPACE] and enemy.can_jump():
                # Прыжок
                enemy.move(y=-60)

            elif enemy.climbing:
                # Если герой на лестнице...

                if pygame.key.get_pressed()[pygame.K_UP]:
                    # двигаем наверх
                    enemy.move(y=-10)

                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    # двигаем вниз
                    enemy.move(y=10)

    if enemy and not enemy.climbing:
        # Если персонаж не на лестнице, на него действует гравитация
        enemy.move(y=FALLING_SPEED)

    # Отрисовываем всё. что необходимо
    screen.fill(BACKGROUND_COLOR)
    platforms.draw(screen)
    ladders.draw(screen)
    en.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

# Выходим из pygame по завершении игрового цикла
pygame.quit()
