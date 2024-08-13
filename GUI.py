from pygame import Rect
from pygame import transform
from pygame import draw
from pygame import image
from pygame import Surface

from pygame.font import Font

from typing import Callable

class VisualElement:
    '''
    Base class for all visual elements.
    '''

    def __init__(self, 
                 x: int, 
                 y: int,
                 width: int = None, 
                 height: int = None,
                 color: tuple[int, int, int] = (255, 255, 255),
                 alpha: int = 255):
        
        self.x = x
        self.y = y

        self.rect = Rect(x, y, width, height)
        
        self.surface = Surface((width, height))
        self.surface.fill(color)
        self.surface.set_alpha(alpha)
    
    
    def resize(self, width: int = None, height: int = None):
        old_surface = self.surface.copy()
        
        self.surface = Surface((width or old_surface.get_width(), height or old_surface.get_height()))
        self.surface.fill(old_surface.get_colorkey())
        self.surface.set_alpha(old_surface.get_alpha())


    def set_surface(self, surface: Surface):
        self.surface = transform.scale(surface, (self.surface.get_width(), self.surface.get_height()))
    
    
    def move(self, x: int = None, y: int = None):
        old_rect = self.rect.copy()
        self.rect = Rect(x or old_rect.x, y or old_rect.y, old_rect.width, old_rect.height)

    def hover(self, pos):
        '''
        Check if the mouse is hovering the element.
        '''
        return self.rect.collidepoint(pos)
    
    
    def draw(self, screen: Surface):
        '''
        Draws the element on the screen.
        '''
        screen.blit(self.surface, (self.rect.x, self.rect.y))


class ImageButton(VisualElement):
    '''
    A button that displays an image. Performs an action when clicked.
    The image is resized to fit the button's size.
    '''

    def __init__(self, x: int, y: int, width: int, height: int, image: Surface):
        super().__init__(x, y, width, height)
        super().set_surface(image)
        self.on_click: Callable = None


class PatternSlider(VisualElement):
    '''
    A slider used to select a pattern. Patterns are displayed one at a time
    and can be cycled through. ImageButtons are used to navigate the slider.
    '''
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)

        self.size = size

        self.patterns = []
        self.names = []

        self.index = 0

        buttons_size = self.size // 2
        self.prev_button = ImageButton(
            self.x - buttons_size,
            self.y + buttons_size,
            buttons_size,
            buttons_size,
            image.load('assets/img/back-bttn.png'))
        self.prev_button.on_click = self.previous

        self.next_button = ImageButton(
            self.x + self.size + buttons_size,
            self.y + buttons_size,
            buttons_size,
            buttons_size,
            image.load('assets/img/next-bttn.png'))
        self.next_button.on_click = self.next

        self.font = Font('assets/font/Pixellari.ttf', 16)

    def add_pattern(self, pattern):
        '''
        Add a pattern to the slider.
        '''
        self.patterns.append(pattern)
        
        self.names.append(
            self.font.render(pattern.name, True, (255, 255, 255))
        )

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

    def draw_layout(self, screen):
        '''
        Draw the layout of the selected item.
        '''
        x = self.rect.x
        y = self.rect.y
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

    def move(self, x: int = None, y: int = None):
        x_offset = (x or 0) - self.rect.x
        y_offset = (y or 0) - self.rect.y
        
        super().move(x, y)
        for element in [self.next_button, self.prev_button]:
            element.move(element.rect.x + x_offset, element.rect.y + y_offset)
        

    def draw(self, screen):
        '''
        Draw the slider on the screen.
        '''

        self.draw_layout(screen)

        self.prev_button.draw(screen)
        self.next_button.draw(screen)
        
        screen.blit(
            self.names[self.index], 
            (self.rect.x + (self.size // 2) - (self.names[self.index].get_width() // 2), 
            self.rect.y + self.size + 10))


class Panel(VisualElement):
    '''
    A background panel that contains other elements inside of it and can slide up.
    The elements contained within the Panel will be moved with it.
    '''
    def __init__(self, x: int, y: int, width: int, height: int, color, alpha):
        super().__init__(x, y, width, height, color, alpha)
        
        self.elements: list[VisualElement] = []
        
        self.hover_rect = Rect(x, y - height, width, height)
        
        self.down_slide_limit = self.rect.y
        self.up_slide_limit = y - height     
        
    
    def add_element(self, element: VisualElement):
        self.elements.append(element)
    
    
    def slide(self, amount, forward: bool = False):
        if self.can_slide():
            amount = -amount if forward else amount
            self.move(y = self.rect.y + amount)
            # Checks to see if the panel overstepped the boundaries
            if not self.can_slide():
                closest_edge = self.up_slide_limit if forward else self.down_slide_limit
                self.move(y=closest_edge)
                
    
    def move(self, x: int = None, y: int = None):        
        x_offset = (x or 0) - self.rect.x
        y_offset = (y or 0) - self.rect.y
        
        super().move(x, y)
        for element in self.elements:
            element.move(element.rect.x + x_offset, element.rect.y + y_offset)


    def can_slide(self):
        return self.rect.y >= self.up_slide_limit and self.rect.y <= self.down_slide_limit


    def hover(self, pos):
        return self.hover_rect.collidepoint(pos)


class MenuBar(VisualElement):
    '''
    A MenuBar is a panel at the top of the screen that contains several menus.
    Each menu has it's own set of menu items.
    The menus are displayed horizontally in the order they were added.
    '''
    def __init__(self, width, height, color):
        super().__init__(0, 0, width, height, color)

        self.menus = []
        self.active_menu = None

    def add_menu(self, menu):
        '''
        Adds a menu to the MenuBar and calculates it's position.
        '''
        self.menus.append(menu)

        curr_x = self.x
        pad = 10
        for menu in self.menus:
            menu.x = curr_x + pad // 2
            menu.y = self.y + (self.surface.get_height() // 4)
            menu._position_items()

            curr_x += menu.text.get_width() + pad
    
    def clicked(self, pos):
        '''
        Determines wich menu on the bar was clicked. Or if none were clicked.
        This method is called per mouse click.
        '''

        x, y = pos

        if y > self.surface.get_height():
            self.active_menu = False
            return
        
        pad = 10
        for menu in self.menus:            
            if x < menu.x + menu.text.get_width() + pad:
                if self.active_menu:
                    self.active_menu.is_active = False
                self.active_menu = menu
                self.active_menu.is_active = True
                return
        
        self.active_menu = False

    def draw(self, screen):
        '''
        Render the MenuBar on the screen.
        '''
        super().draw(screen)

        for menu in self.menus:
            screen.blit(menu.text, (menu.x, menu.y))
        
        if self.active_menu:
            self.active_menu.draw(screen)


class Menu():
    '''
    A Menu is a list of menu items that perform actions when clicked.
    The items are displayed vertically in the order they were added.

    A Menu is meant to be used in a MenuBar.
    '''

    def __init__(self, text):
        self.x = None
        self.y = None
        
        self.font = Font('assets/font/Pixellari.ttf', 18)

        self.text = self.font.render(text, True, (255, 255, 255))
        self.items = []

        self.background = None

        self.is_active = False
    
    def add_item(self, item):
        '''
        Adds an item to the menu. If the item is another Menu, the item
        becomes a submenu. If it is a MenuItem, the item is a clickable
        button.
        '''
        # TODO: check if item is Menu or MenuItem
        item.default_text = self.font.render(item.text, True, (255, 255, 255))
        item.hover_text = self.font.render(item.text, True, (100, 120, 175))
        
        item.text = item.default_text

        self.items.append(item)

    def _position_items(self):
        '''
        Private function that position all of the menu's items.
        Called after the y value of the MenuBar is passed to the Menu. 
        '''
        curr_y = self.y + self.text.get_height() + 10
        max_width = 0
        
        for item in self.items:
            item.x = self.x + 5
            item.y = curr_y
            
            if item.text.get_width() > max_width:
                max_width = item.text.get_width()

            curr_y += item.text.get_height() + 15
        
        for item in self.items:
            item.width = max_width

        self.background = Panel(
            self.x, self.y + self.text.get_height(), max_width + 15, 
            curr_y - (self.y + self.text.get_height()) - 10,
            (11, 20, 26), 255)

    def draw(self, screen):
        self.background.draw(screen)
        for item in self.items:
            screen.blit(item.text, (item.x, item.y))


class MenuItem():
    '''
    A MenuItem works like a button in the sense that it performs an action when clicked.
    '''
    def __init__(self, text):
        self.x = None
        self.y = None
        self.width = None

        self.text = text

        self.default_text = None
        self.hover_text = None
    
    def hover(self, pos):
        x, y = pos
        if x > self.x and x < self.x + self.width:
            if y > self.y and y < self.y + self.text.get_height() + 5:
                return True
        return False