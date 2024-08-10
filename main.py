import pygame
import os

import rle
from life import Grid

from GUI import ImageButton
from GUI import PatternSlider
from GUI import Panel
from GUI import Menu
from GUI import MenuBar
from GUI import MenuItem


from threading import Thread

# Game settings
CELLS_W = 150
CELLS_H = 150
CELL_SIZE = 6
BTTN_SLIDE_SPEED = 0.2
THREADS_COUNT = 2
MENUBAR_H = 4

# Colors
colors = {
    'avery': (11, 20, 26)
}


def check_menu(mouse_pos, menu):
    '''
    Checks if the mouse is hovering over a menu item.
    '''

    if menu.active_menu:
            for item in menu.active_menu.items:
                if item.hover(mouse_pos):
                    item.text = item.hover_text
                else:
                    item.text = item.default_text


def check_buttons(mouse_pos, buttons, bottom_panel, slider_ships, pattern, dt):
    '''
    Checks if the mouse is hovering over the bottom panel, and if so, slides it up.
    '''

    if (mouse_pos[1] > (CELLS_H * CELL_SIZE - 110) and not pattern):
        if (buttons['reload'].y > (CELLS_H * CELL_SIZE) - 75):
            bottom_panel.y = bottom_panel.y - (BTTN_SLIDE_SPEED * dt)
            for button in buttons:
                buttons[button].y = buttons[button].y - (BTTN_SLIDE_SPEED * dt)
            slider_ships.y = slider_ships.y - (BTTN_SLIDE_SPEED * dt)
    else:
        if (buttons['reload'].y < (CELLS_H * CELL_SIZE) + 50):
            bottom_panel.y = bottom_panel.y + (BTTN_SLIDE_SPEED * dt)
            for button in buttons:
                buttons[button].y = buttons[button].y + (BTTN_SLIDE_SPEED * dt)
            slider_ships.y = slider_ships.y + (BTTN_SLIDE_SPEED * dt)


def main():
    # Setup the grid
    cells = Grid(CELL_SIZE, CELLS_W, CELLS_H, 0, MENUBAR_H)

    # load the images
    icons = {
        'play': pygame.image.load('assets/img/play-bttn.png'),
        'pause': pygame.image.load('assets/img/pause-bttn.png'),
        'reload': pygame.image.load('assets/img/reload-bttn.png'),
        'clear': pygame.image.load('assets/img/clear-bttn.png'),
        'pencil': pygame.image.load('assets/img/pencil-bttn.png')
    }

    # Setup the buttons
    buttons = {        
        'pause': ImageButton(
            (CELLS_W * CELL_SIZE // 2) - 100, (CELLS_H * CELL_SIZE) + 50, 50, 
            icons['pause']),
        
        'reload': ImageButton(
            (CELLS_W * CELL_SIZE // 2) - 25, (CELLS_H * CELL_SIZE) + 50, 50, 
            icons['reload']),
        
        'clear': ImageButton(
            (CELLS_W * CELL_SIZE // 2) + 50, (CELLS_H * CELL_SIZE) + 50, 50, 
            icons['clear']),
        
        'pencil': ImageButton(
            50, (CELLS_H * CELL_SIZE) + 50, 50,
            icons['pencil'])
    }

    # Setup the pattern slider
    slider_ships = PatternSlider(
        (CELLS_W * CELL_SIZE) - 120, (CELLS_H * CELL_SIZE) + 50, 50)

    # Setup the bottom panel
    bottom_panel = Panel(
        0, (CELLS_H * CELL_SIZE) + 20, (CELLS_W * CELL_SIZE), 160, colors['avery'], 250)

    # Setup the menu
    menu = MenuBar(CELLS_W * CELL_SIZE, MENUBAR_H * CELL_SIZE, colors['avery'])
    
    menu_file = Menu('File')
    menu_edit = Menu('Fill')
    
    menu_file.add_item(MenuItem('Clear Grid'))

    menu_edit.add_item(MenuItem('Perlin Noise'))
    menu_edit.add_item(MenuItem('Wavelet Noise'))
    menu_edit.add_item(MenuItem('Simplex Noise'))
    menu_edit.add_item(MenuItem('OpenSimplex Noise'))

    menu.add_menu(menu_file)
    menu.add_menu(menu_edit)

    # Load the patterns
    for file in os.listdir('patterns'):
        pattern = rle.decode('patterns/' + file)
        slider_ships.add_pattern(pattern)

    # Initialize pygame
    pygame.init()

    # Create the window
    screen = pygame.display.set_mode(
        (CELLS_W * CELL_SIZE, (CELLS_H * CELL_SIZE) + (MENUBAR_H * CELL_SIZE)))

    # Set the window title
    pygame.display.set_caption('Game of Life')

    # Set the clock
    clock = pygame.time.Clock()

    pattern = None
    
    paused = False
    drawing_mode = False
    
    threads = []

    # Main loop
    while True:
        # Set the FPS
        dt = clock.tick(60)

        # Check the mouse position
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        # Start the threads
        panel_thread = Thread(
            target=check_buttons, 
            args=(mouse_pos, buttons, bottom_panel, slider_ships, pattern, dt))
        
        mouse_thread = Thread(
            target=check_menu, 
            args=(mouse_pos, menu))
  
        mouse_thread.start()
        panel_thread.start()

        threads.append(mouse_thread)
        threads.append(panel_thread)

        if not paused:
            # Calculate the neighbors
            for i in range(THREADS_COUNT):
                thread = Thread(target=cells.calculate_neighbors, args=(i, THREADS_COUNT))
                thread.start()
                threads.append(thread)

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                # Check if the space bar is pressed
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    buttons['pause'].set_image(icons['play'] if paused else icons['pause'])
                    continue

            # If the mouse is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                # TODO: MenuItem clicked action
                if menu.active_menu:
                    pass

                # If mouse clicked reload button
                if buttons['reload'].clicked(mouse_pos):
                    cells = Grid(CELL_SIZE, CELLS_W, CELLS_H, 0, MENUBAR_H)
                    continue

                # If mouse clicked pause button
                if buttons['pause'].clicked(mouse_pos):
                    paused = not paused
                    buttons['pause'].set_image(icons['play'] if paused else icons['pause'])
                    continue

                # If mouse clicked clear button
                if buttons['clear'].clicked(mouse_pos):
                    cells.clear()
                    continue

                # If mouse clicked pencil button
                if buttons['pencil'].clicked(mouse_pos):
                    drawing_mode = False if drawing_mode else True

                # If slider's next button was clicked
                if slider_ships.next_button.clicked(mouse_pos):
                    slider_ships.next()

                # If slider's previous button was clicked
                if slider_ships.prev_button.clicked(mouse_pos):
                    slider_ships.previous()

                # If the user has selected a pattern
                if pattern and not slider_ships.clicked(mouse_pos):
                    x, y = mouse_pos
                    x = (x // CELL_SIZE) - pattern.size
                    y = ((y // CELL_SIZE) - MENUBAR_H) - pattern.size

                    cells.insert_pattern(pattern, x, y)
                    pattern = None

                # If slider was clicked
                if slider_ships.clicked(mouse_pos) and not pattern:
                    pattern = slider_ships.selected()

                # If the program is in drawing mode
                if drawing_mode:
                    x, y = mouse_pos
                    x = (x // CELL_SIZE)
                    y = (y // CELL_SIZE) - MENUBAR_H

                    cells.revive_cell(x, y)
                
                # Check if mouse clicked on the menu
                menu.clicked(mouse_pos)
        
        # Mouse dragging to drawing mode
        if drawing_mode and mouse_pressed:
            x, y = mouse_pos
            x = (x // CELL_SIZE)
            y = (y // CELL_SIZE) - MENUBAR_H

            cells.revive_cell(x, y)

        # Wait for all the threads to finish
        for thread in threads:
            thread.join()
        threads = []

        screen.fill((0, 0, 0))

        # Update and draw the cells
        cells.evolve(screen)
                
        # Draw the held pattern
        if pattern:
            # TODO: fix preview not matching actual placed pattern
            x, y = pygame.mouse.get_pos()
            x = x - (pattern.size * CELL_SIZE)
            y = (y - (pattern.size * CELL_SIZE)) + MENUBAR_H
            pattern.draw(screen, x, y, CELL_SIZE)

        # Draw the bottom panel
        bottom_panel.draw(screen)

        # Draw the buttons
        for button in buttons.values():
            button.draw(screen)

        # Draw the pattern slider
        slider_ships.draw(screen)

        # Draw the menu
        menu.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()