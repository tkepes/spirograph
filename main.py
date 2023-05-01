import numpy as np

from Draw import Draw
from Spirograph import Spirograph
import pygame as pg
import pygame_widgets
from pygame.locals import *
from utils import normalise

FPS = 100
WIDTH, HEIGHT = 2000, 2000
LINE_WIDTH = 2
DYNAMIC_SHADING = True
MY_COLOUR_SCHEME = True
COLOURING_SCHEME_TYPE = 'base'  # anything for the original, 'ribbon' for ribbon, 'base' for base
BIPOLAR_COLOUR_SCHEME = False
ADAPTIVE_RATE = True
BACKGROUND = (0, 0, 0)  # (31, 0, 10)  # (127, 0, 31)
POINTS = []
COLOURS = []
"""
    the whole class of curves that this program is able to display can be decomposed into three components:
        the base curve,
        a spirograph-like curling component which results in a ribbon-like band in place of the sole line of the base curve
        and a radius curve which adds big waves to the now band-like line of the curve
    t will denote the measure of rotation vs time
    Let's take a closer look:
        (B) the base curve (lissajous or some other type): (b_x(t), b_y(t)) e.g. (cos(t), sin(t)), or (2cos(t), sin(2t)), etc,
        (C) the curls: (c_x(t), c_y(t)) e.g. (cos(s*t), sin(s*t)) where s expresses the difference in the rotational speeds
            of the base curve and the curls-curve,
        (R) the radius curve is either a factor of the linear combination of the other two:
          R(t) = R_0 (C r(q t) + 1 - C) where c in [0, 1] expresses the strength of the waving effect, i.e. when C = 0,
            R(t) is simply R_0. E.g. r(q t + b) = sin(q t + b) or r(t) = 4 min((q t + b) % 1, (-(q t + b)) % 1) - 1,
            here q + 1 will amount to the number of larger waves along the base curve
          or alternatively the radius curve can be expressed as dynamic shift which is added onto the curve:
          R_2(t) = (r_x(t), r_y(t)), e.g. (r_x(t), r_y(t)) = C r(q t + b) (db_y(t + d), -db_x(t + d))
            which adjust the waves exactly to the curvature of the base curve (r(t) as in the previous case)
    thus the whole curve can be written as R(t, x(t), y(t)), based on type of the radius R(t, x(t), y(t)) = R(t)(x(t), y(t))
    or R(t, x(t), y(t)) = (R_0 x(t) + r_x(t), R_0 y(t) + r_y(t)),
        x(t) = b_x(t) + (r_0:R_0)c_x(t), y(t) = b_x(t) + (r_0:R_0)c_x(t) where r_0 is the radius of the curls-curve,
        (b_x(t), b_y(t)) = (A_b cos(a_b t + b_b), B_b sin(c_b t + d_b)),
        (c_x(t), c_y(t)) = (A_c cos(a_c t + b_c), B_c sin(c_c t + d_c)),
        R(t) = R_0 (C r(q t + b_r) + 1 - C),
        and (r_x(t), r_y(t)) = C r(q t + b_r) (db_y(t + d_r), -db_x(t + d_r))
            with r(q t + b_r) = sin(q t + b_r) or r(q t + b_r) = 4 min((q t + b_r) % 1, (-(q t + b_r)) % 1) - 1
"""
q = 20  # 20
C = 0.75  # 0.85
speed = 30.05  # 7.12  # 20.05
base_a = 1  # 4
base_b = 0  # np.pi / 2
base_c = 2  # 3
rad_ratio = 8
base_A = 2
base_curve = {'A': base_A, 'a': base_a, 'b': base_b, 'B': 1, 'c': base_c, 'd': 0}
ribbon_curve = {'R div r': rad_ratio, 'speed': speed, 'A': 1, 'a': 1, 'b': 0, 'B': 1, 'c': 1, 'd': 0}
radius_curve = {'C': C, 'q': q, 'b': 0}
curves = [base_curve, ribbon_curve, radius_curve]
curve_codes = ['b', 'c', 'r']
params = {(key + (curve_codes[i] + '_') if key in 'ABabcd' else ''): curves[i][key] for i in range(len(curve_codes)) for
          key in curves[i].keys()}
defaults = {key: 0 if key[0] == 'b' else 1 for key in params.keys()}
defaults['q'] = 1
defaults['speed'] = 1
defaults['R div r'] = 0
defaults['C'] = -1


def get_name():
    keys = ['R div r', 'speed', 'q', 'C', 'A_b', 'A_c', 'B_b', 'B_c', 'a_b', 'a_c', 'c_b', 'c_c', 'b_b', 'b_c', 'd_b',
            'd_c']
    name = ''
    for key in keys:
        if params[key] != defaults[key]:
            name += ', ' + key + (' = {' + (':.2f' if params[key] % 1 > 0.01 else '') + '}').format(params[key])
    return name


def get_colour(spirog, colour=np.array([255, 127, 0])):
    if MY_COLOUR_SCHEME:
        dx, dy = spirog.get_derivatives(COLOURING_SCHEME_TYPE)
        dx, dy = normalise(dx, dy)
        z = 1 * np.sin(spirog.t)
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
    if DYNAMIC_SHADING:
        dx, dy = spirog.get_derivatives(type=COLOURING_SCHEME_TYPE)
        d = (dx ** 2 + dy ** 2) ** 0.5
        d = (d / max([d, spirog.get_max_diff(type=COLOURING_SCHEME_TYPE) * 0.9])) ** 1
        # print(d)
        strength = 0.6
        colour = np.round(strength * (1 / strength - (1 - d)) * colour).astype(int)
    return tuple(colour)


def main():
    pg.init()
    pg.font.init()
    global base_curve, ribbon_curve, radius_curve
    spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, base_curve=base_curve,
                       ribbon_curve=ribbon_curve, radius_curve=radius_curve, rad_type='', ORTHOGONAL_WAVES=True)
    draw = Draw(width=WIDTH, height=HEIGHT, DISPLAY=True, SAVE_IMAGE=True, BACKGROUND=BACKGROUND, LINE_WIDTH=2,
                name=get_name())
    # DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
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
                i = 1
                draw.screen.fill(BACKGROUND)
                while i < len(POINTS):
                    pg.draw.line(draw.screen, COLOURS[i - 1], POINTS[i - 1], POINTS[i], width=LINE_WIDTH)
                    i += 1
                pg.display.update()
                pass
            elif event.type == VIDEOEXPOSE:  # handles window minimising/maximising
                # screen.fill((0, 0, 0))
                # screen.blit(pygame.transform.scale(pic, screen.get_size()), (0, 0))
                # pygame.display.update()
                pass

        x0, y0 = x, y
        x, y = spiro.update()
        POINTS += [(x, y)]
        colour = get_colour(spiro)
        COLOURS += [colour]
        draw.draw_window(x0, y0, x, y, colour=colour)
        pygame_widgets.update(events)
    pg.quit()
    draw.save(name=get_name(), final_save=True)


if __name__ == '__main__':
    main()
