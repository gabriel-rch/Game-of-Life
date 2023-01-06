import pygame
import os

from life import Grid

from GUI import ImageButton
from GUI import PatternSlider

from rle import Decoder

from threading import Thread

# Game settings
CELLS_W = 150
CELLS_H = 150
CELL_SIZE = 6
BTTN_SLIDE_SPEED = 0.2
THREADS_COUNT = 2

def main():
    # Setup the grid
    cells = Grid(CELL_SIZE, CELLS_W, CELLS_H)

    # load the images
    icons = {
        'play': pygame.image.load('assets/play-bttn.png'),
        'pause': pygame.image.load('assets/pause-bttn.png'),
        'reload': pygame.image.load('assets/reload-bttn.png'),
        'clear': pygame.image.load('assets/clear-bttn.png')
    }

    # Setup the buttons
    bttn_pause = ImageButton(
        (CELLS_W * CELL_SIZE // 2) - 100, (CELLS_H * CELL_SIZE) + 50, 50)
    bttn_pause.set_image(icons['pause'])

    bttn_reload = ImageButton(
        (CELLS_W * CELL_SIZE // 2) - 25, (CELLS_H * CELL_SIZE) + 50, 50)
    bttn_reload.set_image(icons['reload'])

    bttn_clear = ImageButton(
        (CELLS_W * CELL_SIZE // 2) + 50, (CELLS_H * CELL_SIZE) + 50, 50)
    bttn_clear.set_image(icons['clear'])

    # Setup the pattern slider
    slider_ships = PatternSlider(
        (CELLS_W * CELL_SIZE) + 100, 100, 50)

    for file in os.listdir('patterns'):
        pattern = Decoder('patterns/' + file).decode()
        slider_ships.add_pattern(pattern)

    # Initialize pygame
    pygame.init()

    # Create the window
    screen = pygame.display.set_mode(
        (CELLS_W * CELL_SIZE, CELLS_H * CELL_SIZE))

    # Set the window title
    pygame.display.set_caption('Game of Life')

    # Set the clock
    clock = pygame.time.Clock()

    pattern = None
    paused = False

    threads = []

    # Main loop
    while True:
        # Set the FPS
        dt = clock.tick(30)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # Check if the mouse is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If mouse clicked reload button
                if bttn_reload.get_rect().collidepoint(event.pos):
                    cells = Grid(CELL_SIZE, CELLS_W, CELLS_H)
                    continue

                # If mouse clicked pause button
                if bttn_pause.get_rect().collidepoint(event.pos):
                    paused = not paused
                    bttn_pause.set_image(icons['play'] if paused else icons['pause'])
                    continue

                # If mouse clicked clear button
                if bttn_clear.get_rect().collidepoint(event.pos):
                    cells.clear()
                    continue

                # If slider's next button was clicked
                if slider_ships.next_button.get_rect().collidepoint(event.pos):
                    slider_ships.next()

                # If slider's previous button was clicked
                if slider_ships.prev_button.get_rect().collidepoint(event.pos):
                    slider_ships.previous()

                # If slider was clicked
                if slider_ships.get_rect().collidepoint(event.pos):
                    pattern = slider_ships.selected()

                # TODO: put this in a button (maybe revive cell button)
                x, y = pygame.mouse.get_pos()
                x = x // CELL_SIZE
                y = y // CELL_SIZE

                cells.revive_cell(x, y)

            # Check if the mouse is released
            if event.type == pygame.MOUSEBUTTONUP:
                if pattern:
                    # TODO: fix out of bounds pattern insertion
                    x, y = pygame.mouse.get_pos()
                    
                    x = (x - (pattern.size * CELL_SIZE)) // CELL_SIZE
                    y = (y - (pattern.size * CELL_SIZE)) // CELL_SIZE

                    cells.insert_pattern(pattern, x, y)
                    pattern = None

        screen.fill((0, 0, 0))

        if not paused:
            for i in range(THREADS_COUNT):
                thread = Thread(target=cells.calculate_neighbors, args=(i, THREADS_COUNT))
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join()

            # Calculate the neighbors
            #cells.calculate_neighbors()

        # Update and draw the cells
        cells.evolve(screen)

        # Slide the buttons in and out
        if (pygame.mouse.get_pos()[1] > (CELLS_H * CELL_SIZE - 200)):
            if (bttn_reload.y > (CELLS_H * CELL_SIZE) - 75):
                bttn_reload.y = bttn_reload.y - (BTTN_SLIDE_SPEED * dt)
                bttn_pause.y = bttn_pause.y - (BTTN_SLIDE_SPEED * dt)
                bttn_clear.y = bttn_clear.y - (BTTN_SLIDE_SPEED * dt)
        else:
            if (bttn_reload.y < (CELLS_H * CELL_SIZE) + 50):
                bttn_reload.y = bttn_reload.y + (BTTN_SLIDE_SPEED * dt)
                bttn_pause.y = bttn_pause.y + (BTTN_SLIDE_SPEED * dt)
                bttn_clear.y = bttn_clear.y + (BTTN_SLIDE_SPEED * dt)

        # Slide the pattern slider in and out
        if (pygame.mouse.get_pos()[0] > (CELLS_W * CELL_SIZE - 200)):
            if (slider_ships.x > (CELLS_W * CELL_SIZE) - 100):
                slider_ships.x = slider_ships.x - (
                    BTTN_SLIDE_SPEED * dt)
        else:
            if (slider_ships.x < (CELLS_W * CELL_SIZE) + 100):
                slider_ships.x = slider_ships.x + (
                    BTTN_SLIDE_SPEED * dt)

        # Draw the held pattern
        if pattern:
            x, y = pygame.mouse.get_pos()
            x = x - (pattern.size * CELL_SIZE)
            y = y - (pattern.size * CELL_SIZE)
            pattern.draw(screen, x, y, CELL_SIZE)

        # Draw the buttons
        bttn_reload.draw(screen)
        bttn_pause.draw(screen)
        bttn_clear.draw(screen)

        # Draw the pattern slider
        slider_ships.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()
