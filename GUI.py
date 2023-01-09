from pygame import Rect
from pygame import transform
from pygame import draw
from pygame import image
from pygame import Surface

from pygame.font import Font
from pygame.font import init as init_font

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
            self.x - (self.size // 2) - 10,
            self.y + (self.size // 4),
            self.size // 2)
        self.prev_button.set_image(image.load('assets/back-bttn.png'))

        self.next_button = ImageButton(
            self.x + self.size + 10,
            self.y + (self.size // 4),
            self.size // 2)
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
        # TODO: center the pattern in the slider (horizontally)
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

        self.next_button.y = self.y + (self.size // 4)
        self.prev_button.y = self.y + (self.size // 4)

        self.next_button.draw(screen)
        self.prev_button.draw(screen)


class Panel (VisualElement):
    '''
    A simple background panel.
    '''
    def __init__(self, x, y, width, height, color, alpha):
        super().__init__(x, y, {'w': width, 'h': height})
        self.panel = Surface((self.size['w'], self.size['h']))
        self.panel.fill(color)
        self.panel.set_alpha(alpha)

    def draw(self, screen):
        '''
        Draw the panel on the screen.
        '''
        screen.blit(self.panel, (self.x, self.y))


class MenuBar (VisualElement):
    def __init__(self, width, height, color):
        super().__init__(0, 0, {'w': width, 'h': height})
        self.background = Panel(0, 0, self.size['w'], self.size['h'], color, 255)
        
        init_font()
        self.font = Font('assets/Pixellari.ttf', 18)

        self.items = []

    def add_item(self, itm):
        itm.text = self.font.render(itm.text, True, (255, 255, 255))
        self.items.append(itm)

        curr_x = self.x
        pad = 10
        for item in self.items:
            item.x = curr_x + pad // 2
            item.y = self.y + (self.size['h'] // 4)
            
            curr_x += item.text.get_width() + pad
    
    def draw(self, screen):
        self.background.draw(screen)

        for item in self.items:
            screen.blit(item.text, (item.x, item.y))


class MenuItem():
    def __init__(self, text):
        self.x = None
        self.y = None
        
        self.text = text
        