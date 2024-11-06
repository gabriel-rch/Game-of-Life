import pygame
import os

import rle

from life import Grid
from life import Pattern

from GUI import ImageButton
from GUI import PatternSlider
from GUI import Panel
from GUI import Menu
from GUI import MenuBar
from GUI import MenuItem

from threading import Thread
from typing import Tuple


class GameOfLife:
    def __init__(self, grid_size: Tuple[int, int] = (150, 150), cell_size: int = 6):
        self.grid_width, self.grid_height = grid_size
        self.cell_size = cell_size
        
        self.colors = {
            'avery': (11, 20, 26)
        }
        
        self.paused = False
        self.drawing_mode = False
        
        # Setup the grid
        self.cells = Grid(cell_size, self.grid_width, self.grid_height, 0, 4)

        # load the images
        self.icons = {
            'play': pygame.image.load('assets/img/play-bttn.png'),
            'pause': pygame.image.load('assets/img/pause-bttn.png'),
            'reload': pygame.image.load('assets/img/reload-bttn.png'),
            'clear': pygame.image.load('assets/img/clear-bttn.png'),
            'pencil': pygame.image.load('assets/img/pencil-bttn.png'),
            'cursor': pygame.image.load('assets/img/cursor-bttn.png'),
        }
        
        # Setup the buttons
        self.pause_button = ImageButton((self.grid_width * cell_size // 2) - 100, (self.grid_height * cell_size) + 50, 50, 50, self.icons['pause'])
        self.pause_button.on_click = self.button_pause_clicked
        
        self.reload_button = ImageButton((self.grid_width * cell_size // 2) - 25, (self.grid_height * cell_size) + 50, 50, 50, self.icons['reload'])
        self.reload_button.on_click = self.button_reload_clicked
        
        self.clear_button = ImageButton((self.grid_width * cell_size // 2) + 50, (self.grid_height * cell_size) + 50, 50, 50, self.icons['clear'])
        self.clear_button.on_click = self.button_clear_clicked
        
        self.cursor_button = ImageButton(50, (self.grid_height * cell_size) + 50, 50, 50, self.icons['cursor'])
        self.cursor_button.on_click = self.button_cursor_clicked        
        
        # Setup the pattern slider
        self.slider_ships = PatternSlider(
            (self.grid_width * cell_size) - 120, (self.grid_height * cell_size) + 50, 50)

        # Setup the bottom panel
        self.bottom_panel = Panel(0, (self.grid_height * cell_size) + 25, (self.grid_width * cell_size), 120, self.colors['avery'], 250)
        for element in [self.pause_button, self.clear_button, self.reload_button, self.cursor_button, self.slider_ships]:
            self.bottom_panel.add_element(element)

        # Setup the menu
        self.menu = MenuBar(self.grid_width * cell_size, 4 * cell_size, self.colors['avery'])
        
        self.menu_file = Menu('File')
        self.menu_edit = Menu('Fill')
        
        self.menu_file.add_item(MenuItem('Clear Grid'))

        self.menu_edit.add_item(MenuItem('Perlin Noise'))
        self.menu_edit.add_item(MenuItem('Wavelet Noise'))
        self.menu_edit.add_item(MenuItem('Simplex Noise'))
        self.menu_edit.add_item(MenuItem('OpenSimplex Noise'))

        self.menu.add_menu(self.menu_file)
        self.menu.add_menu(self.menu_edit)

        # Load the patterns
        for file in os.listdir('patterns'):
            pattern = rle.decode('patterns/' + file)
            self.slider_ships.add_pattern(pattern)
        
        # Run setup after all elements have been created
        self.setup()
    
    def setup(self):
        elements = vars(self).items()
                
        self.clickables = []
        self.clickables.extend([button for _, button in elements if isinstance(button, ImageButton)])
        self.clickables.extend([slider.next_button for _, slider in elements if isinstance(slider, PatternSlider)])
        self.clickables.extend([slider.prev_button for _, slider in elements if isinstance(slider, PatternSlider)])
    
    
    def button_reload_clicked(self):
        self.cells = Grid(self.cell_size, self.grid_width, self.grid_height, 0, 4)
        
    
    def button_pause_clicked(self):
        self.paused = not self.paused
        self.pause_button.set_surface(self.icons['play'] if self.paused else self.icons['pause'])
    
    
    def button_clear_clicked(self):
        self.cells.clear()
        
    
    def button_cursor_clicked(self):
        if self.drawing_mode:
            self.cursor_button.set_surface(self.icons['cursor'])
            self.drawing_mode = False
        else:
            self.cursor_button.set_surface(self.icons['pencil'])
            self.drawing_mode = True
    
    
    def check_menu(self, mouse_pos, menu):
        '''
        Checks if the mouse is hovering over a menu item.
        '''
        if menu.active_menu:
                for item in menu.active_menu.items:
                    if item.hover(mouse_pos):
                        item.text = item.hover_text
                    else:
                        item.text = item.default_text
    

    def start(self):
        # Create the window
        screen = pygame.display.set_mode((self.grid_width * self.cell_size, (self.grid_height * self.cell_size) + (4 * self.cell_size)))
        pygame.display.set_caption('Game of Life') 
        
        clock = pygame.time.Clock()
        
        pattern: Pattern = None
        threads = []
        
        # Main loop
        while True:
            # Set the FPS
            dt = clock.tick(60)

            # Check the mouse position
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]

            # Start the threads
            mouse_thread = Thread(
                target=self.check_menu, 
                args=(mouse_pos, self.menu))
            mouse_thread.start()
            threads.append(mouse_thread)

            if not self.paused:
                # Calculate the neighbors
                for i in range(4):
                    thread = Thread(target=self.cells.calculate_neighbors, args=(i, 4))
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
                        self.button_pause_clicked()
                        continue
                    # Check if the 'r' key is pressed
                    if event.key == pygame.K_r:
                        self.button_reload_clicked()
                        continue

                    # Check if the 'c' key is pressed
                    if event.key == pygame.K_c:
                        self.button_clear_clicked()
                        continue

                # If the mouse is clicked
                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    for clickable in self.clickables:
                        if clickable.hover(mouse_pos):
                            clickable.on_click()

                    # If slider was clicked
                    if self.slider_ships.hover(mouse_pos) and pattern is None:
                        pattern = self.slider_ships.selected()

                    # If the user has selected a pattern
                    if pattern is not None and not self.slider_ships.hover(mouse_pos):
                        x, y = mouse_pos
                        x = (x // self.cell_size) - pattern.size
                        y = ((y // self.cell_size) - 4) - pattern.size

                        self.cells.insert_pattern(pattern, x, y)
                        pattern = None                    

                    # If the program is in drawing mode
                    if self.drawing_mode:
                        x, y = mouse_pos
                        x = (x // self.cell_size)
                        y = (y // self.cell_size) - 4

                        self.cells.revive_cell(x, y)
                    
                    # Check if mouse clicked on the menu
                    self.menu.hover(mouse_pos)
            
            # Slide the panels
            slide_forward = self.bottom_panel.hover(mouse_pos) and pattern is None
            self.bottom_panel.slide(int(0.2*dt), forward=slide_forward)
        
            # Mouse dragging to drawing mode
            if self.drawing_mode and mouse_pressed:
                x, y = mouse_pos
                x = (x // self.cell_size)
                y = (y // self.cell_size) - 4

                self.cells.revive_cell(x, y)

            # Wait for all the threads to finish
            for thread in threads:
                thread.join()
            threads = []

            screen.fill((0, 0, 0))

            # Update and draw the cells
            self.cells.evolve(screen)
                    
            # Draw the held pattern
            if pattern is not None:
                x, y = pygame.mouse.get_pos()
                x = x - (pattern.size * self.cell_size)
                y = (y - (pattern.size * self.cell_size)) + 4
                                
                pattern.draw(screen, x, y, self.cell_size)

            # Draw the bottom panel
            self.bottom_panel.draw(screen)

            # Draw the buttons
            for clickable in self.clickables:
                clickable.draw(screen)

            # Draw the pattern slider
            self.slider_ships.draw(screen)

            # Draw the menu
            self.menu.draw(screen)

            pygame.display.update()


if __name__ == '__main__':
    pygame.init()
    game = GameOfLife()
    game.start()