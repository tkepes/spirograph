import pygame as pg
from PIL import Image, ImageDraw
from pygame_widgets.button import Button
import pygame_widgets
from pygame.locals import *
import numpy as np
from Image import MyImage

DISPLAY_WIDTH = 1500
DISPLAY_HEIGHT = 1000


class Draw:
    def __init__(self, width=1000, height=1000, DISPLAY=True, SAVE_IMAGE=True, BACKGROUND=(0, 0, 0), LINE_WIDTH=2):
        pg.init()
        pg.font.init()
        self.width = width
        self.height = height
        self.DISPLAY = DISPLAY
        self.SAVE_IMAGE = SAVE_IMAGE
        self.BACKGROUND = BACKGROUND
        self.line_width = LINE_WIDTH
        if self.SAVE_IMAGE:
            self.im = MyImage(self.width, self.height, BACKGROUND=self.BACKGROUND)
            self.im.fill(colour=self.BACKGROUND)
        if self.DISPLAY:
            global DISPLAY_WIDTH, DISPLAY_HEIGHT
            self.w_ratio = DISPLAY_WIDTH / self.width
            self.h_ratio = DISPLAY_HEIGHT / self.height
            self.resize_ratio = min(self.w_ratio, self.h_ratio)
            print(self.w_ratio, self.h_ratio)
            self.screen = pg.display.set_mode((round(self.w_ratio * self.width), round(self.h_ratio * self.height)),
                                              RESIZABLE)
            if self.SAVE_IMAGE:
                self.SAVE = Button(self.screen, 50, DISPLAY_HEIGHT - 75, 75, 25, text='Save now!',  # Text to display
                                   fontSize=12,  # Size of font
                                   margin=2,  # Minimum distance between text/image and edge of button
                                   inactiveColour=(200, 50, 0),  # Colour of button when not being interacted with
                                   hoverColour=(150, 0, 0),  # Colour of button when being hovered over
                                   pressedColour=(0, 200, 20),  # Colour of button when being clicked
                                   radius=20,  # Radius of border corners (leave empty for not curved)
                                   onClick=lambda: self.im.save(main=False)  # Function to call when clicked on
                                   )
            self.screen.fill(self.BACKGROUND)

    def DrawWindow(self, x0, y0, x, y, colour=(255, 127, 0)):
        if self.SAVE_IMAGE:
            self.im.line(x0, y0, x, y, colour=colour)
        if self.DISPLAY:
            # print((self.w_ratio * x, self.h_ratio * y), (self.w_ratio * x0, self.h_ratio * y0))
            cx = max(DISPLAY_WIDTH - self.resize_ratio * self.width, 0) // 2
            cy = max(DISPLAY_HEIGHT - self.resize_ratio * self.height, 0) // 2
            x0, y0 = cx + self.resize_ratio * x0, cy + self.resize_ratio * y0
            x, y = cx + self.resize_ratio * x, cy + self.resize_ratio * y
            pg.draw.line(self.screen, colour, (x0, y0), (x, y), width=self.line_width)
            pg.display.update()
            pygame_widgets.update(pg.event.get())

    def save(self, name='', main=False):
        if self.SAVE_IMAGE:
            self.im.save(name=name, main=main)
