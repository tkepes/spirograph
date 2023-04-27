from utils import create_folder, euclidean
from datetime import datetime as dt
import numpy as np
import pygame as pg
from PIL import Image, ImageDraw
from pygame_widgets.button import Button
import pygame_widgets
from pygame.locals import *

pg.init()
pg.font.init()
PATH = str(dt.today().date())
stage = 0
# x = A * R0 * cos(at) + B * r0 * cos(bwt)
# y = C * R0 * sin(ct) - D * r0 * sin(dwt)

WIDTH, HEIGHT = 1000, 1000
LINE_WIDTH = 2
DYNAMIC_COLOURING = True
MY_COLOUR_SCHEME = True
BIPOLAR_COLOUR_SCHEME = False
ADAPTIVE_RATE = True

screen = pg.display.set_mode((WIDTH, HEIGHT), RESIZABLE)
SAVE = Button(screen, 50, HEIGHT - 75, 75, 25, text='Save now!',  # Text to display
              fontSize=12,  # Size of font
              margin=2,  # Minimum distance between text/image and edge of button
              inactiveColour=(200, 50, 0),  # Colour of button when not being interacted with
              hoverColour=(150, 0, 0),  # Colour of button when being hovered over
              pressedColour=(0, 200, 20),  # Colour of button when being clicked
              radius=20,  # Radius of border corners (leave empty for not curved)
              onClick=lambda: save(main=False)  # Function to call when clicked on
              )
IM = Image.new('RGB', (WIDTH, HEIGHT))
DRAW = ImageDraw.Draw(IM)

BACKGROUND = (0, 0, 0)  # (31, 0, 10)  # (127, 0, 31)

FPS = 100


class Spirograph:
    global WIDTH, HEIGHT

    def __init__(self):
        self.A, self.B, self.C, self.D = 1, 1, 1, 1
        self.a, self.b, self.c, self.d = 1, 1, 1, 1
        self.Tc, self.tc, self.Ts, self.ts = 0, 0, 0, 0
        # self.A = 2
        self.a = 4
        self.c = 3
        self.Tc = np.pi / 2
        self.r0 = 1 * WIDTH // 32  # 100
        self.R0 = min(WIDTH, HEIGHT) // (2 * np.sqrt(max(self.A, self.C))) - 120 - self.r0

        sin = lambda t, a=1, b=0: np.sin(a * t + b)
        cos = lambda t, a=1, b=0: np.cos(a * t + b)
        dsin = lambda t, a=1, b=0: a * cos(t, a, b)
        dcos = lambda t, a=1, b=0: -a * sin(t, a, b)
        # self.x = width // 2 + self.R0 + self.r0
        # self.y = height // 2
        self.q = 20  # 6
        self.speed = 20.05  # 20.05  # 15.12  # 1.02
        self.RC = 0.9
        self.R = lambda t: self.R0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dR = lambda t: self.R0 * (1 - self.RC) * dsin(t, a=self.q)
        self.r = lambda t: self.r0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dr = lambda t: self.r0 * (1 - self.RC) * dsin(t, a=self.q)
        self.r2 = lambda t: 0 * self.r0 ** 3 / self.R0 ** 2 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dr2 = lambda t: 0 * self.r0 ** 3 / self.R0 ** 2 * (1 - self.RC) * dsin(t, a=self.q)
        k = 0
        self.x = lambda t: WIDTH // 2 + self.A * self.R(t) * cos(t, a=self.a, b=self.Tc) + \
                           self.B * self.r(t) * cos(t, a=self.b * self.speed, b=self.tc) + \
                           self.r2(t) * cos(t, a=self.b * self.speed ** 4) + k * self.r0 * (
                                   0 * sin(t, a=12) + cos(t, a=12))
        self.dx = lambda t: self.A * (self.dR(t) * cos(t, a=self.a, b=self.Tc) +
                                      self.R(t) * dcos(t, a=self.a, b=self.Tc)) + \
                            self.B * (self.dr(t) * cos(t, a=self.b * self.speed, b=self.tc) +
                                      self.r(t) * dcos(t, a=self.b * self.speed, b=self.tc)) + \
                            self.r2(t) * dcos(t, a=self.b * self.speed ** 4) + \
                            self.dr2(t) * cos(t, a=self.b * self.speed ** 4)
        self.y = lambda t: HEIGHT // 2 + self.C * self.R(t) * sin(t, self.c, b=self.Ts) - \
                           self.D * self.r(t) * sin(t, a=self.d * self.speed, b=self.ts) + \
                           self.r2(t) * cos(t, a=self.d * self.speed ** 4) + k * self.r0 * (
                                   sin(t, a=12) + 0 * cos(t, a=12))
        self.dy = lambda t: self.C * (self.dR(t) * sin(t, a=self.c, b=self.Ts) +
                                      self.R(t) * dsin(t, a=self.c, b=self.Ts)) - \
                            self.D * (self.dr(t) * sin(t, a=self.d * self.speed, b=self.ts) +
                                      self.r(t) * dsin(t, a=self.d * self.speed, b=self.ts)) + \
                            self.r2(t) * dsin(t, a=self.d * self.speed ** 4) + \
                            self.dr2(t) * sin(t, a=self.d * self.speed ** 4)
        self.phi = lambda t: np.sign(self.dy(t)) * np.arccos(self.dx(t) / np.sqrt(self.dx(t) ** 2 + self.dy(t) ** 2))
        # self.x1 = lambda t: self.x(t) +
        self.t = 0.0
        # self.rate = 0.03  # 31 * np.pi / 41  # 6 * 1e-2
        self.rate = 3 * min(0.08 / self.speed, 0.06)

        # self.x, self.y = self.update()
        def get_period(*nums):
            nums = list(nums)
            while len(nums) > 1:
                j = len(nums) - 1
                while j > 0:
                    a, b = str(nums[j]), str(nums[j - 1])
                    t = 0
                    n2 = [a, b]
                    for c in n2:
                        if '.' in c:
                            t = max(t, len(c[c.index('.') + 1:]))
                    if t > 0:
                        for i in range(2):
                            if '.' not in n2[i]:
                                n2[i] = n2[i] + '0' * t
                            else:
                                n2[i] = n2[i].replace('.', '') + '0' * (t - len(n2[i][n2[i].index('.') + 1:]))
                    a, b = int(n2[0]), int(n2[1])

                    c = a * b // euclidean(a, b) // 10 ** t
                    nums = nums[:j - 1] + [c] + nums[j + 1:]
                    j -= 2
            return nums[0]

        self.per = np.abs(get_period(max(self.q, 1), self.a, self.b * self.speed, self.c, self.d * self.speed))
        print(self.q, self.a, self.b * self.speed, self.c, self.d * self.speed)
        print(self.per)
        if self.per > 10 ** 3:
            m = round(max(self.q, self.a, self.b * self.speed, self.c, self.d * self.speed))
            T = np.linspace(0, m, 10 * m + 1)
        else:
            T = np.linspace(0, self.per, 10 * self.per + 1)
        maxx = max([self.x(t) for t in T])
        minx = min([self.x(t) for t in T])
        maxy = max([self.y(t) for t in T])
        miny = max([self.y(t) for t in T])
        max_ = max(maxx - WIDTH // 2, maxy - HEIGHT // 2, WIDTH // 2 - minx, HEIGHT // 2 - miny)
        m = (min(WIDTH, HEIGHT) // 2 - 120) / max_
        self.R0 *= m
        self.r0 *= m
        dF = [(self.dx(t), self.dy(t)) for t in T]  # np.linspace(0, self.per, 10 * self.per + 1)]
        D = [np.sqrt(dx ** 2 + dy ** 2) for dx, dy in dF]
        self.maxslope = max(D)
        self.avslope = np.average(D)
        print(round(self.maxslope, 2), round(self.avslope, 2))

    def coordinate_functions(self, cos_fact, cos_const, sin_fact, sin_const):
        return lambda t: np.cos(cos_fact * t + cos_const), lambda t: np.sin(sin_fact * t + sin_const)

    def update(self):
        # self.x = width // 2 + self.A * self.R0 * (0.5 * np.sin(3 * self.t) + 0.5) * np.cos(
        #     self.a * self.t + self.Tc) + self.B * self.r0 * np.cos(self.b * self.speed * self.t + self.tc)
        # self.y = height // 2 + self.C * self.R0 * (0.5 * np.sin(3 * self.t) + 0.5) * np.sin(
        #     self.c * self.t + self.Ts) - self.D * self.r0 * np.sin(self.d * self.speed * self.t + self.ts)
        # np.sin(self.speed * self.t)
        if ADAPTIVE_RATE:
            delta = (np.sqrt(self.dx(self.t) ** 2 + self.dy(self.t) ** 2) / self.maxslope)
            delta = np.power(delta, 0.01) / 100
            # print(round(delta, 3))
            self.t += delta
        else:
            self.t += self.rate
        return self.x(self.t), self.y(self.t)

    def get_derivatives(self):
        # dx = -self.a * self.A * self.R0 * np.sin(self.a * self.t + self.Tc) - \
        #      self.b * self.speed * self.B * self.r0 * np.sin(self.b * self.speed * self.t + self.tc)
        # dy = self.c * self.C * self.R0 * np.cos(self.c * self.t + self.Ts) - \
        #      self.d * self.speed * self.D * self.r0 * np.cos(self.d * self.speed * self.t + self.ts)
        # return dx, dy
        return self.dx(self.t), self.dy(self.t)

    def get_params(self):
        return self.A, self.B, self.C, self.D, self.a, self.b, self.c, self.d, self.Tc, self.Ts, self.tc, self.ts


spirog = Spirograph()


def normalise(*nums):
    if len(nums) < 2:
        raise ValueError
    norm = np.sqrt(sum([n ** 2 for n in nums]))
    return [n / norm for n in nums]


def draw_window():
    global x, y, x0, y0
    x0, y0 = x, y
    x, y = spirog.update()
    colour = np.array([255, 127, 0])
    if MY_COLOUR_SCHEME:
        dx, dy = spirog.get_derivatives()
        dx, dy = normalise(dx, dy)
        z = 0 * np.sin(spirog.t)
        # dx, dy, z = normalise(dx, dy, z)
        # d = np.cos(np.pi / 3 * spirog.t)
        # dx, dy, z = dx, dy + d, z + d
        m = min(dx, dy, z)
        dx, dy, z = dx - m, dy - m, z - m
        dx, dy, z = normalise(dx, dy, z)
        colour = np.round(255 * np.array([dx, dy, z])).astype(int)
    elif BIPOLAR_COLOUR_SCHEME:
        v = (1, 0)
        u = (-v[1], v[0])
        col1 = np.array([0, 0, 255])
        col2 = 255 - col1
        dx, dy = spirog.get_derivatives()
        dx, dy = normalise(dx, dy)
        n1 = v[0] * dx + v[1] * dy
        n2 = u[0] * dx + u[1] * dy
        # phi = np.arccos(u[0] * dx + u[1] * dy) / (np.pi)
        # colour = np.round((max(0, phi - 0.5) * col1 + max(0, 0.5 - phi) * col2)).astype(int)
        # colour = np.round((n1 * col1 + n2 * col2) / (max(n1 + n2, 1))).astype(int)
        colour = (n1 * col1 + n2 * col2) / (max(n1 + n2, 1))
        # colour -= np.min(colour)
        colour = np.round(np.maximum(np.minimum(colour, 255), 0)).astype(int)
    if DYNAMIC_COLOURING:
        dx, dy = spirog.get_derivatives()
        d = np.sqrt(dx ** 2 + dy ** 2)
        d = np.power(d / max([d, spirog.maxslope * 0.9]), 1)
        # print(d)
        strength = 0.6
        colour = np.round(strength * (1 / strength - (1 - d)) * colour).astype(int)
    colour = tuple(colour)
    pg.draw.line(screen, colour, (x, y), (x0, y0), width=LINE_WIDTH)
    DRAW.line((x, y, x0, y0), fill=colour, width=LINE_WIDTH)
    pg.display.update()


def parameters_string():
    # x = A * R0 * cos(at) + B * r0 * cos(bwt)
    # y = C * R0 * sin(ct) - D * r0 * sin(dwt)
    # speed = w
    # rate = t_{n+1} - t_n
    st = 'r0 div R0 = {:.2f}, q = {}, rate = {:.2f}, speed = {:.2f}'.format(spirog.r0 / spirog.R0, spirog.q,
                                                                            spirog.rate, spirog.speed)
    args = spirog.get_params()
    for i in range(8):
        if args[i] != 1:
            st += ', ' + 'ABCDabcd'[i] + ' = {:.2f}'.format(args[i])
    for i in range(4):
        if args[i + 8] != 1:
            st += ', ' + 'Tt'[i // 2] + 'cs'[i % 2] + ' = {}'.format(args[i])
    return st


def save(main=False):
    global stage
    stage += 1
    global PATH
    st = parameters_string()
    if not main and len(PATH) == 10:
        PATH = str(dt.today().date()) + '/' + str(dt.today().time())[:8].replace(':', '-') + ' - ' + st
    create_folder(PATH)
    a = len(str(stage))
    if main:
        IM.save(PATH + '/' + (('000'[:3 - a] + str(stage) + ' ') if stage > 1 else '') +
                str(dt.today().time())[:8].replace(':', '-') + (' ' + st if stage == 1 else '') + '.png')
    else:
        IM.save(PATH + '/' + '000'[:3 - a] + str(stage) + ' ' + str(dt.today().time())[:8].replace(':', '-') + '.png')


def main():
    print(parameters_string())
    screen.fill(BACKGROUND)
    DRAW.rectangle([(0, 0), (WIDTH, HEIGHT)], fill=BACKGROUND, outline=BACKGROUND, width=2)
    create_folder(PATH)
    global x, y, x0, y0
    x, y = spirog.update()

    clock = pg.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            elif event.type == VIDEORESIZE:
                # screen.blit(pg.transform.scale(pic, event.dict['size']), (0, 0))
                pg.display.update()
        draw_window()
        pygame_widgets.update(events)
    pg.quit()
    save(main=True)


if __name__ == '__main__':
    main()
