import pygame
import Maplvl
from btn import draw_button
import konstruktor
import game
import sqlite3
import stats

# Задаём все необходимые константы
WINDOW_SIZE = 500, 500
BACKGROUND_COLOR = [255] * 3
BTN_COLOR = (0, 255, 0)


def lvl():
    res = Maplvl.choose_lvl()

    # Обработка выбора
    if res == 'Back':
        # Если возврат, то ломаем цикл (функция запустится вновь)
        return

    elif res == 'Create lvl':
        # Открываем конструктор пользовательского уровня
        konstruktor.konstrukt()
        return
    elif res:
        res = res.replace("User\'s lvl", "0")  # Меняем на номер уровня 0

        # Запускаем нужный уровень
        rec = game.go(int(res))

        if rec:  # Запись рекорда в БД, если он превосходит старый
            con = sqlite3.connect("Map.db")
            cur = con.cursor()
            old_rec = cur.execute(
                f"""SELECT * FROM data WHERE id == {res}""").fetchone()

            if rec < int(old_rec[-1]):
                cur.execute(f"""DELETE FROM data WHERE id == {res}""")
                cur.execute(
                    """INSERT INTO data(id, Platform, Barrel,
                    Ladder, Startpos, Finishpos, record)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    old_rec[:-1] + (rec,))
                con.commit()
                con.close()

    lvl()


def main():
    # Задаём значения кнопок (текст, x, y, длинна, ширина)
    buttons = [
        ["Start", 50, 50, 400, 100, BTN_COLOR],
        ["Exit", 50, 350, 400, 100, BTN_COLOR],
        ["Stats", 50, 200, 400, 100, BTN_COLOR]
    ]

    pygame.init()  # Инициализация

    # Подготовка игрого цикла
    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)
    running = True
    draw_button(screen, buttons)
    pygame.display.flip()
    while running:

        # Обрабатываем каждое событие циклом for
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                # Завершаем функцию (она не перезапустится), если программу закрыли
                return True

            # отслеживание нажатий кнопки
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in buttons:
                        if i[1] < event.pos[0] < i[1] + i[3] and i[2] < event.pos[1] < i[2] + i[4]:
                            # выбор действия при нажатии

                            if i[0] == 'Start':
                                # Переход к меню выбора уровней
                                running = False
                                lvl()

                            elif i[0] == 'Stats':
                                running = False
                                stats.load()

                            elif i[0] == 'Exit':
                                print('Exit')
                                # Функция не запустится вновь
                                return True


if __name__ == '__main__':
    r = main()
    while not r:  # Пока функция не вернёт True, перезапускаем её
        r = main()
    pygame.quit()


