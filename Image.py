from PIL import Image, ImageDraw
from Path import Path


class MyImage:
    def __init__(self, width=1000, height=1000, mode='RGB', BACKGROUND=(0, 0, 0), LINE_WIDTH=2, name=None,
                 st_res=0, st_margin=5):
        self.PATH = Path('Images/')
        self.width = width
        self.height = height
        self.im = Image.new(mode, (self.width, self.height))
        self.draw = ImageDraw.Draw(self.im)
        self.BACKGROUND = BACKGROUND
        self.stage = 0
        self.line_width = LINE_WIDTH
        self.name = name
        self.st_margin = st_margin
        self.st_res = st_res - 2 * self.st_margin
        if self.st_res:
            self.ratio = st_res / max(self.width, self.height)
            self.st_res = round(self.ratio * self.width) + 2 * self.st_margin
            self.st_height = round(self.ratio * self.height) + 2 * self.st_margin
            self.st_im = Image.new(mode, (self.st_res, self.st_height))
            self.st_draw = ImageDraw.Draw(self.st_im)

    def fill(self, colour=None):
        if colour is None:
            colour = self.BACKGROUND
        self.draw.rectangle((0, 0, self.width, self.height), fill=colour, outline=colour, width=2)
        if self.st_res:
            self.st_draw.rectangle((0, 0, self.st_res, self.st_height), fill=colour, outline=colour, width=2)

    def line(self, x0, y0, x, y, colour=(255, 127, 0), width=2):
        self.draw.line((x, y, x0, y0), fill=colour, width=width)  # self.line_width)
        if self.st_res:
            self.st_draw.line((self.ratio * x + self.st_margin, self.ratio * y + self.st_margin,
                               self.ratio * x0 + self.st_margin, self.ratio * y0 + self.st_margin),
                              fill=colour, width=width)

    def save(self, name=None, final_save=False):  # name = parameters_string()
        # self.PATH.reset()
        if name is None:
            name = self.name
        self.stage += 1
        a = len(str(self.stage))
        if final_save:
            self.im.save(self.PATH + '/' + (('000'[:3 - a] + str(self.stage) + ' ') if self.stage > 1 else '') +
                         self.PATH.instant() + (' ' + name if self.stage == 1 else '') + '.png')
        else:
            if len(self.PATH) == 17:
                path = self.PATH.instant() + ' - ' + name
                self.PATH.update(path)
            self.im.save(self.PATH + '/' + '000'[:3 - a] + str(self.stage) + ' ' + self.PATH.instant() + '.png')

