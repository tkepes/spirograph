import numpy as np

from Draw import Draw
from Spirograph import Spirograph
import pygame as pg
import pygame_widgets
from pygame.locals import *
from utils import parameters_string, normalise

FPS = 100
WIDTH, HEIGHT = 2000, 2000
LINE_WIDTH = 2
DYNAMIC_COLOURING = True
MY_COLOUR_SCHEME = True
BIPOLAR_COLOUR_SCHEME = False
ADAPTIVE_RATE = True
BACKGROUND = (0, 0, 0)  # (31, 0, 10)  # (127, 0, 31)
POINTS = []
COLOURS = []


def GetColour(spirog, colour=np.array([255, 127, 0])):
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
    return tuple(colour)


def main():
    pg.init()
    pg.font.init()
    spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE)
    draw = Draw(width=WIDTH, height=HEIGHT, DISPLAY=True, SAVE_IMAGE=True, BACKGROUND=BACKGROUND, LINE_WIDTH=2,
                name=parameters_string(spiro))
    # DYNAMIC_COLOURING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
    x, y = spiro.update()
    global POINTS, COLOURS
    POINTS += [(x, y)]
    clock = pg.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                run = False
            elif event.type == WINDOWRESIZED:
                draw.resized()
            elif event.type == VIDEORESIZE:
                # draw.screen.blit(pg.transform.scale(pic, event.dict['size']), (0, 0))
                # i = 1
                # while i < len(POINTS):
                #     pg.draw.line(draw.screen, COLOURS[i - 1], POINTS[i-1], POINTS[i], width=LINE_WIDTH)
                #     pg.display.update()
                # pg.display.update()
                pass
            elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
                # screen.fill((0, 0, 0))
                # screen.blit(pygame.transform.scale(pic, screen.get_size()), (0, 0))
                # pygame.display.update()
                pass

        x0, y0 = x, y
        x, y = spiro.update()
        POINTS += [(x, y)]
        colour = GetColour(spiro)
        COLOURS += [colour]
        draw.DrawWindow(x0, y0, x, y, colour=colour)
        pygame_widgets.update(events)
    pg.quit()
    draw.save(name=parameters_string(spiro), main=True)


if __name__ == '__main__':
    main()
