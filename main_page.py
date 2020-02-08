import pygame
import Maplvl
from menu import draw_button
import game

# Задаём все необходимые константы
WINDOW_SIZE = 500, 500
BACKGROUND_COLOR = [255] * 3
GREEN = (0, 255, 0)


def main():
    # задаю значения кнопки(текст, x, y, длинна, ширина)(можно добавить картинку кнопки, но яне нашел красивой)
    buttons = [("Start", 50, 50, 400, 100), ('Exit', 50, 350, 400, 100), ('Stats', 50, 200, 400, 100)]

    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)
    running = True
    draw_button(screen, buttons, GREEN)
    pygame.display.flip()
    while running:

        # Обрабатываем каждое событие циклом for
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                # Завершаем игровой цикл, если программу закрыли
                running = False

            # отслеживание нажатий кнопки
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in buttons:
                        if i[1] < event.pos[0] < i[1] + i[3] and i[2] < event.pos[1] < i[2] + i[4]:
                            # выбор действия при нажатии

                            if i[0] == 'Start':
                                running = False
                                res = Maplvl.choose_lvl()

                                if res == 'Back':
                                    return True

                            elif i[0] == 'Stats':
                                pass
                            elif i[0] == 'Exit':
                                running = False
                            pass


if __name__ == '__main__':
    r = main()
    while r:
        r = main()
