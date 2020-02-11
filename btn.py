import pygame

TEXT_FONT_SIZE = 28


def draw_button(screen, buttons):
    """Отрисовка кнопок из переданного списка"""

    for i in buttons:
        pygame.draw.rect(screen, i[-1], (i[1], i[2], i[3], i[4]), 2)
        text = i[0]
        length = i[3]
        height = i[4]
        try:
            int(text)
            font_size = length // len(text)
        except ValueError:
            font_size = TEXT_FONT_SIZE
        myFont = pygame.font.SysFont("Comic Sans MS", font_size)
        myText = myFont.render(text, 1, i[-1])
        screen.blit(myText, ((i[1] + length // 2) - myText.get_width() // 2,
                             (i[2] + height // 2) - myText.get_height() // 2))




