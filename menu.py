import pygame

WINDOW_SIZE = 600, 600
BACKGROUND_COLOR = (255, 255, 255)


# отрисовка кнопок
def draw_button(screen, buttons):
    for i in buttons:
        pygame.draw.rect(screen, (0, 0, 0), (i[1], i[2], i[3], i[4]), 2)
        text = i[0]
        length = i[3]
        height = i[4]
        font_size = int(length // len(text))
        myFont = pygame.font.SysFont("Calibri", font_size)
        myText = myFont.render(text, 1, (0, 0, 0))
        screen.blit(myText, ((i[1] + length / 2) - myText.get_width() / 2,
                             (i[2] + height / 2) - myText.get_height() / 2))


def main():
    # задаю значения кнопки(текст, x, y, длинна, ширина)(можно добавить картинку кнопки, но яне нашел красивой)
    buttons = [('Back', 100, 500, 400, 100)]
    # создание кнопок уровней
    for i in range(5):
        for j in range(5):
            buttons.append((str(i * 5 + j), j * 120 + 20, i * 100, 80, 80))

    pygame.init()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen.fill(BACKGROUND_COLOR)
    running = True
    draw_button(screen, buttons)
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
                            print("print my blanks please")
                            for j in range(25):
                                if i[0] == buttons[j][0]:
                                    print(i[0])
                                    pass

    pygame.quit()


if __name__ == '__main__':
    main()