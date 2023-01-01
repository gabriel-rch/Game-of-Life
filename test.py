import pygame
from GUI import PatternSlider
from life import Pattern

CELLS_W = 150
CELLS_H = 150
CELL_SIZE = 6

pygame.init()
screen = pygame.display.set_mode((CELLS_W * CELL_SIZE, CELLS_H * CELL_SIZE))

slider = PatternSlider(
    (CELLS_W * CELL_SIZE // 2), (CELLS_H * CELL_SIZE // 2), 100)

cross = Pattern([[0, 1, 0],
                 [1, 1, 1],
                 [0, 1, 0]])

big_cross = Pattern([[0, 0, 0, 0, 1, 0, 0, 0, 0],
                     [1, 1, 1, 0, 1, 1, 1, 1, 1],
                     [0, 0, 0, 0, 1, 0, 0, 0, 0],
                     [1, 1, 1, 1, 0, 1, 0, 0, 1],
                     [1, 0, 1, 1, 1, 1, 1, 1, 1],
                     [1, 1, 1, 1, 0, 1, 0, 1, 1],
                     [1, 1, 0, 1, 0, 1, 1, 0, 1],
                     [1, 0, 1, 1, 1, 1, 1, 0, 1],
                     [1, 0, 0, 1, 0, 0, 1, 1, 1]])


slider.add_pattern(cross)
slider.add_pattern(big_cross)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        # Check if the mouse is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If slider's next button was clicked
            if slider.next_button.get_rect().collidepoint(event.pos):
                slider.next()

            # If slider's previous button was clicked
            if slider.previous_button.get_rect().collidepoint(event.pos):
                slider.previous()

            # If slider was clicked
            if slider.get_rect().collidepoint(event.pos):
                pattern = slider.selected()

    screen.fill((0, 0, 0))

    slider.draw(screen)

    pygame.display.update()
