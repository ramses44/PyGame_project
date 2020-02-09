import pygame
import sqlite3
from btn import draw_button as draw

WINDOW_SIZE = 640, 560
BUTTON_COLOR = [0, 255, 0]
BACKGROUND_COLOR = [255]*3
TEXT_COLOR = (0, 128, 0)


def load():
    """Загрузка статистики (рекордов)"""

    # Инициализация
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)
    running = True

    # Кнопка возврата
    back_btn = ["Back", 10, WINDOW_SIZE[1] - 110, WINDOW_SIZE[0] - 20, 100, BUTTON_COLOR]

    # Подключение к БД
    con = sqlite3.connect("Map.db")
    cur = con.cursor()

    # Формируем список кнопок с записанными в них рекордами
    records = []

    btn_width = (WINDOW_SIZE[0] - 40) // 3

    for i in range(10):
        try:
            res = cur.execute(f"""SELECT record FROM data WHERE id == {i}""").fetchone()[-1]
            res = str(res) + " seconds" if res != 10000 else "-"
            if i != 0:
                records.append([f"{i}: {res}", 10 + (i - 1) % 3 * (btn_width + 10),
                                10 + (i - 1) // 3 * 110, btn_width, 100, TEXT_COLOR])
            else:
                records.append([f"User\'s lvl: {res}",
                                10, 340, WINDOW_SIZE[0] - 20, 100, TEXT_COLOR])
        except TypeError:
            records.append([f"{i}: -", 10 + (i - 1) % 3 * (btn_width + 10),
                            10 + (i - 1) // 3 * 110, btn_width, 100, TEXT_COLOR])

    # Отрисовка кнопок
    draw(screen, [back_btn] + records)
    pygame.display.flip()

    # Обработка событий
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and \
                back_btn[1] < event.pos[0] < back_btn[1] + back_btn[3] and \
                back_btn[2] < event.pos[1] < back_btn[2] + back_btn[4]:

                running = False


if __name__ == "__main__":
    load()
