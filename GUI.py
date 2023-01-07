from pygame import Rect
from pygame import transform
from pygame import draw
from pygame import image


class VisualElement:
    '''
    Base class for all visual elements.
    '''
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def get_rect(self):
        '''
        Get the rect of the button.
        '''
        return Rect(
            self.x, self.y,
            self.size, self.size
        )


class ImageButton (VisualElement):
    '''
    A basic button with an image.
    '''
    def __init__(self, x, y, size, image=None):
        super().__init__(x, y, size)

        self.rect = None
        
        if image:
            self.set_image(image)
        else:
            self.image = None

    def set_image(self, image):
        '''
        Set the image of the button.

        Args:
            image (pygame.Surface): The image to use.
        '''
        self.image = transform.scale(image, (self.size, self.size))
        self.rect = Rect(
            self.x, self.y,
            self.image.get_width(), self.image.get_height()
        )

    def draw(self, screen):
        '''
        Draw the button on the screen.
        '''
        screen.blit(self.image, (self.x, self.y))


class PatternSlider (VisualElement):
    '''
    A slider to select an item.
    '''
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

        self.patterns = []
        self.index = 0

        self.prev_button = ImageButton(
            self.x,
            self.y + self.size + 10,
            self.size // 4)
        self.prev_button.set_image(image.load('assets/back-bttn.png'))

        self.next_button = ImageButton(
            self.x + self.size - self.size // 4,
            self.y + self.size + 10,
            self.size // 4)
        self.next_button.set_image(image.load('assets/next-bttn.png'))

    def add_pattern(self, pattern):
        '''
        Add a pattern to the slider.
        '''
        self.patterns.append(pattern)

    def selected(self):
        '''
        Get the selected item.
        '''
        return self.patterns[self.index]

    def next(self):
        '''
        Select the next item.
        '''
        self.index = (self.index + 1) % len(self.patterns)

    def previous(self):
        '''
        Select the previous item.
        '''
        self.index = (self.index - 1) % len(self.patterns)

    def draw_layout(self, x, y, screen):
        current_pattern = self.patterns[self.index]
        cell_size = self.size // current_pattern.size

        for rows in current_pattern.layout:
            for cell in rows:
                if cell:
                    draw.rect(
                        screen,
                        (255, 255, 255),
                        (x, y, cell_size, cell_size))
                x += cell_size
            x = self.x
            y += cell_size

    def draw(self, screen):
        '''
        Draw the slider on the screen.
        '''
        
        self.draw_layout(self.x, self.y, screen)

        self.next_button.x = self.x + self.size - self.size // 4
        self.prev_button.x = self.x

        self.next_button.draw(screen)
        self.prev_button.draw(screen)
