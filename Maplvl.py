import pygame

WINDOW_SIZE = 380, 600
BACKGROUND_COLOR = (255, 255, 255)
UNLOCKED = (0, 255, 0)
LOCKED = [128] * 3


# отрисовка кнопок
def draw_button(screen, buttons):
    for i in buttons:
        pygame.draw.rect(screen, i[-1], (i[1], i[2], i[3], i[4]), 2)
        text = i[0]
        length = i[3]
        height = i[4]
        font_size = int(length // len(text))
        myFont = pygame.font.SysFont("Calibri", font_size)
        myText = myFont.render(text, 1, i[-1])
        screen.blit(myText, ((i[1] + length // 2) - myText.get_width() // 2,
                             (i[2] + height // 2) - myText.get_height() // 2))


def choose_lvl():
    # задаю значения кнопки(текст, x, y, длинна, ширина)(можно добавить картинку кнопки, но яне нашел красивой)
    buttons = [
        ('User\'s lvl', 20, 380, 340, 100, UNLOCKED),
        ('1', 20, 20, 100, 100, UNLOCKED),
        ('2', 140, 20, 100, 100, LOCKED),
        ('3', 260, 20, 100, 100, LOCKED),
        ('4', 20, 140, 100, 100, LOCKED),
        ('5', 140, 140, 100, 100, LOCKED),
        ('6', 260, 140, 100, 100, LOCKED),
        ('7', 20, 260, 100, 100, LOCKED),
        ('8', 140, 260, 100, 100, LOCKED),
        ('9', 260, 260, 100, 100, LOCKED),
    ]
    # создание кнопок уровней

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
                            for j in range(25):
                                if i[0] == buttons[j][0]:
                                    return i[0]


if __name__ == "__main__":
    choose_lvl()
