import pygame as pg
from pygame_widgets.button import Button
import pygame_widgets
from pygame.locals import *
from Image import MyImage


class Draw:
    def __init__(self, width=1000, height=1000, DISPLAY=True, SAVE_IMAGE=True, BACKGROUND=(0, 0, 0), LINE_WIDTH=2,
                 DISPLAY_WIDTH=1500, DISPLAY_HEIGHT=1000, name=''):
        self.width = width
        self.height = height
        self.DISPLAY = DISPLAY
        self.SAVE_IMAGE = SAVE_IMAGE
        self.BACKGROUND = BACKGROUND
        self.line_width = LINE_WIDTH
        if self.SAVE_IMAGE:
            self.name = name
            self.im = MyImage(self.width, self.height, BACKGROUND=self.BACKGROUND, name=self.name)
            self.im.fill(colour=self.BACKGROUND)
        if self.DISPLAY:
            self.DISPLAY_WIDTH = DISPLAY_WIDTH
            self.DISPLAY_HEIGHT = DISPLAY_HEIGHT
            pg.init()
            pg.font.init()
            self.update_display_ratio()
            self.screen = pg.display.set_mode((round(self.w_ratio * self.width), round(self.h_ratio * self.height)),
                                              RESIZABLE)
            if self.SAVE_IMAGE:
                c = round(self.DISPLAY_HEIGHT * 0.075)
                self.SAVE = Button(self.screen, 2 * c // 3, self.DISPLAY_HEIGHT - c, c, c // 3, text='Save now!',
                                   # Text to display
                                   fontSize=c // 6,  # Size of font
                                   margin=2,  # Minimum distance between text/image and edge of button
                                   inactiveColour=(200, 50, 0),  # Colour of button when not being interacted with
                                   hoverColour=(150, 0, 0),  # Colour of button when being hovered over
                                   pressedColour=(0, 200, 20),  # Colour of button when being clicked
                                   radius=20,  # Radius of border corners (leave empty for not curved)
                                   onClick=lambda: self.im.save(final_save=False)  # Function to call when clicked on
                                   )
            self.screen.fill(self.BACKGROUND)

    def update_display_ratio(self):
        self.w_ratio = self.DISPLAY_WIDTH / self.width
        self.h_ratio = self.DISPLAY_HEIGHT / self.height
        self.resize_ratio = min(self.w_ratio, self.h_ratio)

    def resized(self):
        self.DISPLAY_WIDTH = self.screen.get_width()
        self.DISPLAY_HEIGHT = self.screen.get_height()
        self.update_display_ratio()
        if self.SAVE_IMAGE:
            self.SAVE.hide()
            # self.SAVE.disable()
            c = round(self.DISPLAY_HEIGHT * 0.075)
            button_width = max(c, 40)
            button_height = max(c // 3, 15)
            self.SAVE = Button(self.screen, 2 * c // 3, self.DISPLAY_HEIGHT - max(c, button_height + 2), button_width,
                               button_height,
                               text='Save now!',  # Text to display
                               fontSize=max(c // 6, 10),  # Size of font
                               margin=2,  # Minimum distance between text/image and edge of button
                               inactiveColour=(200, 50, 0),  # Colour of button when not being interacted with
                               hoverColour=(150, 0, 0),  # Colour of button when being hovered over
                               pressedColour=(0, 200, 20),  # Colour of button when being clicked
                               radius=20,  # Radius of border corners (leave empty for not curved)
                               onClick=lambda: self.im.save(final_save=False)  # Function to call when clicked on
                               )

    def draw_window(self, x0, y0, x, y, colour=(255, 127, 0)):
        if self.SAVE_IMAGE:
            self.im.line(x0, y0, x, y, colour=colour)
        if self.DISPLAY:
            # print((self.w_ratio * x, self.h_ratio * y), (self.w_ratio * x0, self.h_ratio * y0))
            cx = max(self.DISPLAY_WIDTH - self.resize_ratio * self.width, 0) // 2
            cy = max(self.DISPLAY_HEIGHT - self.resize_ratio * self.height, 0) // 2
            x0, y0 = cx + self.resize_ratio * x0, cy + self.resize_ratio * y0
            x, y = cx + self.resize_ratio * x, cy + self.resize_ratio * y
            pg.draw.line(self.screen, colour, (x0, y0), (x, y), width=self.line_width)
            pg.display.update()
            pygame_widgets.update(pg.event.get())

    def save(self, name=None, final_save=False):
        if name is None:
            name = self.name
        if self.SAVE_IMAGE:
            self.im.save(name=name, final_save=final_save)
