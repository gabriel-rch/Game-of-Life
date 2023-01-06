import pygame
import random


class Cell:
    '''
    A cell is a spot in the grid that can be alive or dead.
    The cell's state is determined by the number of live neighbors it has.

    The rules are such that any live cell with:
        2 or 3 live neighbors will stay alive.
        less than 2 live neighbors will die, due to underpopulation.
        more than 3 live neighbors will die, due to overpopulation.
    And any dead cell with exactly 3 live neighbors will become alive,
    due to reproduction.

    Attributes:
        x (int): The x coordinate of the cell.
        y (int): The y coordinate of the cell.
        alive (bool): The current state of the cell.
        next_status (bool): The next state of the cell.
        neighbors (list): A list of all valid neighbors.
    '''
    def __init__(self, x, y, size, alive):
        self.x = x
        self.y = y

        self.size = size
        self.color = (x, y, 100)

        self.alive = alive
        self.next_status = alive

        self.neighbors = []

    # Calculate the number of live neighbors
    def calculate_neighbors(self):
        '''
        Calculate the number of live neighbors of the cell.
        '''
        live_neighbors = 0
        for neighbor in self.neighbors:
            live_neighbors = live_neighbors + neighbor.alive

        # Apply the rules
        if self.alive:
            if live_neighbors < 2 or live_neighbors > 3:
                self.next_status = False
        else:
            if live_neighbors == 3:
                self.next_status = True

    # Update the cell status
    def evolve(self):
        '''
        Update the cell status.
        '''
        self.alive = self.next_status

    # Draw the cell
    def draw(self, screen):
        '''
        Draw the cell on the screen, if it is alive.

        Args:
            screen (pygame.Surface): The screen to draw on.
        '''
        if self.alive:
            pygame.draw.rect(
                screen,
                self.color,
                (self.x * self.size, self.y * self.size, self.size, self.size))


class Grid:
    def __init__(self, cell_size, cells_w, cells_h):
        self.cells = [[Cell(x, y, cell_size, bool(random.getrandbits(1)))
                      for y in range(cells_h)]
                      for x in range(cells_w)]

        for row in self.cells:
            for cell in row:
                self.define_neighbors(cell)

    def define_neighbors(self, cell):
        x, y = cell.x, cell.y
        for i in range(-1, 2):
            for j in range(-1, 2):
                # Ignore the current cell
                if not (i == j == 0) \
                   and 0 <= x + i < len(self.cells) \
                   and 0 <= y + j < len(self.cells[0]):
                    cell.neighbors.append(self.cells[x + i][y + j])

    def calculate_neighbors(self, current_thread = 0, total_threads = 1):
        start = current_thread * ((len(self.cells) ** 2) // total_threads)
        stop = (current_thread + 1) * ((len(self.cells) ** 2) // total_threads)
 
        for i in range(start, stop):
            self.cells[i // len(self.cells)][i % len(self.cells)].calculate_neighbors()

    def evolve(self, surface):
        for row in self.cells:
            for cell in row:
                cell.evolve()
                cell.draw(surface)

    def insert_pattern(self, pattern, x, y):
        for i in range(pattern.size):
            for j in range(pattern.size):
                self.cells[x + j][y + i].alive = pattern.at(i, j)
                self.cells[x + j][y + i].next_status = pattern.at(i, j)

    def revive_cell(self, x, y):
        self.cells[x][y].alive = True
        self.cells[x][y].next_status = True

    def clear(self):
        for row in self.cells:
            for cell in row:
                cell.alive = False
                cell.next_status = False


class Pattern:
    def __init__(self, name, layout: list = [[bool]]):
        self.name = name
        self.layout = layout
        self.size = len(layout)

    def at(self, x, y):
        return self.layout[x][y]
    
    def draw(self, screen, x, y, size):
        # TODO: fix out of bounds cell color
        for i in range(self.size):
            for j in range(self.size):
                if self.at(i, j):
                    pygame.draw.rect(
                        screen,
                        (((x + j) // size) % 255, ((y + i) // size) % 255, 100),
                        (x + j * size, y + i * size, size, size))

