from PIL import Image, ImageDraw
from Path import Path
from Name import Name

class MyImage:
    def __init__(self, im=None, width=1000, height=1000, mode='RGB', BACKGROUND=(0, 0, 0), LINE_WIDTH=2, name=None,
                 st_im=None, st_res=0, st_margin=5, path=None):
        self.PATH = Path('Images/')
        if path is not None:
            self.PATH.path = path
        if im is None:
            self.width, self.height = width, height
            self.im = Image.new(mode, (self.width, self.height))
        else:
            self.im = im
            self.width, self.height = self.im.width, self.im.height
        self.draw = ImageDraw.Draw(self.im)
        self.BACKGROUND = BACKGROUND
        self.stage = 0
        self.line_width = LINE_WIDTH
        self.name = name
        self.st_res = st_res
        if self.st_res:
            self.st_margin = st_margin
            if st_im is not None:
                self.st_res = st_im.width
                self.st_height = st_im.height
                self.ratio = (self.st_res - 2 * self.st_margin) / max(self.width, self.height)
                self.st_im = st_im
            else:
                self.st_res -= 2 * self.st_margin
                self.ratio = self.st_res / max(self.width, self.height)
                self.st_res = round(self.ratio * self.width) + 2 * self.st_margin
                self.st_height = round(self.ratio * self.height) + 2 * self.st_margin
                self.st_im = Image.new(mode, (self.st_res, self.st_height))
            self.st_draw = ImageDraw.Draw(self.st_im)
        if im is None:
            self.fill()

    def fill(self, colour=None):
        if colour is None:
            colour = self.BACKGROUND
        self.draw.rectangle((0, 0, self.width, self.height), fill=colour, outline=colour, width=2)
        if self.st_res:
            self.st_draw.rectangle((0, 0, self.st_res, self.st_height), fill=colour, outline=colour, width=2)

    def line(self, x0, y0, x, y, colour=(255, 127, 0), width=0):
        if width == 0:
            width = self.line_width
        self.draw.line((x, y, x0, y0), fill=colour, width=width)  # self.line_width)
        if self.st_res:
            self.st_draw.line((self.ratio * x + self.st_margin, self.ratio * y + self.st_margin,
                               self.ratio * x0 + self.st_margin, self.ratio * y0 + self.st_margin),
                              fill=colour, width=width)

    def save(self, name=None, final_save=False):  # name = parameters_string()
        if name is None:
            name = self.name
        if name == 'temp':
            self.im.save('Images/temp.png')
            if self.st_res:
                self.st_im.save('Images/temp_st.png')
        else:
            name, self.stage = Name(self.PATH).get_name(name, self.stage, final_save)
            self.im.save(name)

    def get_save_name(self, name=None, final_save=False):
        if name is None:
            name = self.name
        a = len(str(self.stage + 1))
        if name == 'temp':
            return 'Images/temp.png'
        elif final_save:
            return self.PATH + '/' + (
                ('000'[:3 - a] + str(self.stage + 1) + ' ') if self.stage > 0 else '') + self.PATH.instant() + (
                ' ' + name if self.stage == 0 else '') + '.png'
        else:
            if len(self.PATH) == 17:
                path = self.PATH.instant() + ' - ' + name
                self.PATH.update(path)
            return self.PATH + '/' + '000'[:3 - a] + str(self.stage + 1) + ' ' + self.PATH.instant() + '.png'
