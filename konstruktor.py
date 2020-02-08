from menu import draw_button
from game import *
import sqlite3

BLACK = [0]*3
BUTTON_COLOR = [0, 255, 0]
BACKGROUND_COLOR = [255]*3


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

    def move(self, x, y):
        self.rect.x, self.rect.y = x, y


def savemap(num, platforms, barrels, ladders):
    """Функция сохранения карты в БД"""

    con = sqlite3.connect('Map.db')
    cur = con.cursor()

    # Num = str(1)  # пока и так сойдет  # Нет, не сойдёт
    plat = []  # Карооче, если ты это увидишь просто напиши мне их позиции (и угл у панелек) ИЛИ напиши мне в личку это.
    bar = []
    lad = []
    startpos = '0,0'
    finishpos = '100,100'

    for sprite in platforms:
        plat.append(str(sprite.rect.x) + ',' + str(sprite.rect.y) + ':' + str(sprite.angle))

    for sprite in barrels:
        bar.append(str(sprite.rect.x) + ',' + str(sprite.rect.y))

    for sprite in ladders:
        lad.append(str(sprite.rect.x) + ',' + str(sprite.rect.y))

    print(num, ';'.join(plat), ';'.join(bar), ';'.join(lad), startpos, finishpos)

    cur.execute("INSERT INTO data(id, Platform, Barrel, Ladder, Startpos, Finishpos) VALUES (?, ?, ?, ?, ?, ?)",
                (num, ';'.join(plat), ';'.join(bar), ';'.join(lad), startpos, finishpos))

    con.commit()
    con.close()


def start(screen):
    """Функция запускающая окно коснтруктора уровней"""

    # Кнопка сохранения
    btn = ["Создать", 10, 10, 200, 80]

    # Это для выбора элемента, который мы ставим кнопкой мыши
    selected = None
    examples_rects = {
        'platform': (250, 5, PLATFORM_SIZE[0] + 10, PLATFORM_SIZE[1] + 10),
        'ladder': (450, 5, LADDER_SIZE[0] + 10, LADDER_SIZE[1] + 10),
        'barrel': (520, 5, BARREL_SIZE[0] + 10, BARREL_SIZE[1] + 10),
                }

    # Группы спрайтов
    examples = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    ladders = pygame.sprite.Group()
    barrels = pygame.sprite.Group()
    poses = pygame.sprite.Group()

    # Образцы
    Platform(examples, (examples_rects['platform'][0] + 5, examples_rects['platform'][1] + 5))
    Ladder(examples, (examples_rects['ladder'][0] + 5, examples_rects['ladder'][1] + 5))
    Barrel(examples, (examples_rects['barrel'][0] + 5, examples_rects['barrel'][1] + 5))

    start_ = StartPos(poses, (5, WINDOW_SIZE[1] // 2 - 20))
    finish_ = FinishPos(poses, (WINDOW_SIZE[0] - 350, WINDOW_SIZE[1] // 2 - 20))

    running = True
    choosing_start = False
    choosing_finish = False
    screen.fill(BACKGROUND_COLOR)
    draw_selected = lambda: None

    while running:  # Цикл-обработчик
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                # Завершаем игровой цикл, если программу закрыли
                running = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN:

                obj = pygame.sprite.spritecollideany(Nothing(pygame.mouse.get_pos()), poses)

                if type(obj) == StartPos:
                    choosing_start = not choosing_start
                    continue
                elif type(obj) == FinishPos:
                    choosing_finish = not choosing_finish
                    continue

                obj = pygame.sprite.spritecollideany(Nothing(pygame.mouse.get_pos()), examples)

                if type(obj) == Platform:
                    draw_selected = lambda: pygame.draw.rect(screen, BLACK, examples_rects['platform'], 2)
                    selected = Platform, platforms
                elif type(obj) == Ladder:
                    draw_selected = lambda: pygame.draw.rect(screen, BLACK, examples_rects['ladder'], 2)
                    selected = Ladder, ladders
                elif type(obj) == Barrel:
                    draw_selected = lambda: pygame.draw.rect(screen, BLACK, examples_rects['barrel'], 2)
                    selected = Barrel, barrels

                if not selected or obj:
                    continue

                if btn[1] < event.pos[0] < btn[1] + btn[3] and \
                        btn[2] < event.pos[1] < btn[2] + btn[4]:

                    savemap('0', platforms, barrels, ladders)
                    running = False
                    break

                selected[0](selected[1], event.pos)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_DELETE:
                    for group in [platforms, ladders, barrels]:
                        obj = pygame.sprite.spritecollideany(Nothing(pygame.mouse.get_pos()), group)
                        if obj:
                            obj.kill()
                            break

                elif event.key == pygame.K_LALT:
                    obj = pygame.sprite.spritecollideany(Nothing(pygame.mouse.get_pos()), platforms)
                    if obj:
                        obj.rotate(30)

        if choosing_start:
            start_.move(*pygame.mouse.get_pos())
        if choosing_finish:
            finish_.move(*pygame.mouse.get_pos())

        screen.fill(BACKGROUND_COLOR)
        draw_button(screen, [btn], BUTTON_COLOR)
        draw_selected()
        examples.draw(screen)
        platforms.draw(screen)
        ladders.draw(screen)
        barrels.draw(screen)
        poses.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((700, 500))
    start(screen)
    pygame.quit()
