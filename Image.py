from PIL import Image, ImageDraw
from Path import Path
import numpy as np


class MyImage:
    def __init__(self, width=1000, height=1000, mode='RGB', BACKGROUND=(0, 0, 0), LINE_WIDTH=2, name=None):
        self.PATH = Path('Images/')
        self.width = width
        self.height = height
        self.im = Image.new(mode, (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)
        self.BACKGROUND = BACKGROUND
        self.stage = 0
        self.line_width = LINE_WIDTH
        self.name = name

    def fill(self, colour=None):
        if colour is None:
            colour = self.BACKGROUND
        self.draw.rectangle([(0, 0), (self.width, self.height)], fill=colour, outline=colour, width=2)

    def line(self, x0, y0, x, y, colour=np.array([255, 128, 0]), width=2):
        colour = tuple(colour)
        self.draw.line((x, y, x0, y0), fill=colour, width=width)  # self.line_width)

    def save(self, name=None, final_save=False):  # name = parameters_string()
        # self.PATH.reset()
        if name is None:
            name = self.name
        self.stage += 1
        if not final_save and len(self.PATH) == 17:
            path = self.PATH.instant() + ' - ' + name
            self.PATH.update(path)
        a = len(str(self.stage))
        if final_save:
            self.im.save(self.PATH + '/' + (('000'[:3 - a] + str(self.stage) + ' ') if self.stage > 1 else '') +
                         self.PATH.instant() + (' ' + name if self.stage == 1 else '') + '.png')
        else:
            self.im.save(self.PATH + '/' + '000'[:3 - a] + str(self.stage) + ' ' + self.PATH.instant() + '.png')
