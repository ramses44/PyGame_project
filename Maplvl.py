import pygame
import sqlite3
from btn import draw_button

WINDOW_SIZE = 380, 600
BACKGROUND_COLOR = (255, 255, 255)
UNLOCKED = (0, 255, 0)
LOCKED = [128] * 3


def choose_lvl():
    # задаю значения кнопки(текст, x, y, длинна, ширина)(можно добавить картинку кнопки, но яне нашел красивой)
    buttons = [
        ['User\'s lvl', 20, 380, 160, 100, LOCKED],
        ['1', 20, 20, 100, 100, LOCKED],
        ['2', 140, 20, 100, 100, LOCKED],
        ['3', 260, 20, 100, 100, LOCKED],
        ['4', 20, 140, 100, 100, LOCKED],
        ['5', 140, 140, 100, 100, LOCKED],
        ['6', 260, 140, 100, 100, LOCKED],
        ['7', 20, 260, 100, 100, LOCKED],
        ['8', 140, 260, 100, 100, LOCKED],
        ['9', 260, 260, 100, 100, LOCKED],
        ['Create lvl', 200, 380, 160, 100, UNLOCKED],
        ['Back', 20, 500, 340, 70, UNLOCKED]
    ]

    # Делаем доступными уровни, которые есть в БД
    con = sqlite3.connect("Map.db")
    cur = con.cursor()

    available_lvls = cur.execute("""SELECT id FROM data""").fetchall()

    for num in available_lvls:
        buttons[num[0]][-1] = UNLOCKED

    # создание кнопок уровней

    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)
    draw_button(screen, buttons)
    pygame.display.flip()
    while True:
        # Обрабатываем каждое событие циклом for
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Завершаем игровой цикл, если программу закрыли
                return "Back"
            # отслеживание нажатий кнопки
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in buttons:
                        if i[1] < event.pos[0] < i[1] + i[3] and i[2] < event.pos[1] < i[2] + i[4]:
                            # выбор действия при нажатии
                            for j in range(12):
                                if i[0] == buttons[j][0]:
                                    return i[0] if i[-1] == UNLOCKED else None


if __name__ == "__main__":
    choose_lvl()



