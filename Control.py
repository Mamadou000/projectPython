import pygame
from colors import GREEN, RED, GREY

class Toggle():
    # A Toggle is a yes or no (boolean) control
    def __init__(self,x,y,defualt,config_key):
        self.rect = pygame.Rect(x, y, 280,70)
        self.value = defualt # Is the toggle on?
        self.color = GREEN if self.value == True else RED

        # The value to change in the configuration
        self.config_key = config_key

        self.active = False
        self.is_button = False
    
    def handle_key(self, key):
        return
    
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            # Flip the value
            self.value = not self.value

            # Flip the color to show whether it's on or off
            if self.value:
                self.color = GREEN
            else:
                self.color = RED

            # Tell the Game that this parameter changed
            return True
        
        # This didn't change
        return False

    def draw(self, panel, fonts):
        pygame.draw.rect(panel.control_window, self.color, self.rect)
        panel.text_render(panel.control_window, str(self.config_key), fonts["toggle"], (self.rect.x+1,self.rect.y+1),background=self.color)
        if self.active:
            pygame.draw.rect(panel.control_window, (255, 255, 255), self.rect, 3)

class NumericControl():
    # A NumericControl is a control to deal with numbers within a range
    def __init__(self,x,y,default,increment,min_val,max_val,config_key,is_int=False):
        # down_rect is the hitbox to lower the value, and up_rect is for increase
        self.rect = pygame.Rect(x, y, 280, 70)

        self.value = default

        self.is_int = is_int

        # How much the value increases and decreases by
        self.increment = increment
        self.max = max_val
        self.min = min_val
        self.config_key = config_key

        self.active = False

        self.buffer_value = str(self.value)

        self.is_button = False
    
    def handle_key(self, key):
        if not self.active:
            return
        
        if key == "BACKSPACE":
            if len(self.buffer_value) == 0:
                return
            self.buffer_value = self.buffer_value[:-1]
            return

        self.buffer_value += str(key)
    
    def check_click(self,pos):
        if self.rect.collidepoint(pos):
            self.active = not self.active
            # Keep value within bounds
            if not self.active:
                if self.buffer_value == "":
                    self.active = True
                    return not self.active

                self.value = float(self.buffer_value)
                if self.is_int:
                    self.value = int(self.value)
                if self.value > self.max:
                    self.value = self.max
                if self.value < self.min:
                    self.value = self.min

            return not self.active
        return False
    
    def draw(self, panel, fonts):
        pygame.draw.rect(panel.control_window, GREY, self.rect)
        panel.text_render(panel.control_window, str(self.config_key), fonts["numDescription"], (self.rect.x+1,self.rect.y+1),background=GREY)
        panel.text_render(panel.control_window, str(self.buffer_value), fonts["numValue"], (self.rect.x+25,self.rect.y+20),background=GREY)
        if self.active:
            pygame.draw.rect(panel.control_window, (255, 255, 255), self.rect, 3)

class Button:
    def __init__(self,x,y,color,action,text):
        self.rect = pygame.Rect(x, y, 280, 70)
        self.color = color
        self.action = action
        self.text = text

        self.active = False
        self.is_button = True
    
    def handle_key(self, key):
        return
    
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            # Use this Button
            self.action()
        
        # Buttons don't need to show they've completed their action
        return False

    def draw(self, panel, fonts):
        pygame.draw.rect(panel.control_window, self.color, self.rect)
        panel.text_render(panel.control_window, str(self.text), fonts["button"], (self.rect.x+1,self.rect.y+1),background=self.color)
        if self.active:
            pygame.draw.rect(panel.control_window, (255, 255, 255), self.rect, 3)