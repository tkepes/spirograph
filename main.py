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
COLOURING_SCHEME_TYPE: str = '(base+curls)_'
# '' for the whole curve, 'curls_' for curls, 'base_' for base, 'rad_' for the radius,
# '(base+curls)_' for the whole curve without the radius, '(base+rad)_' for the whole curve without the curls
BIPOLAR_COLOUR_SCHEME = False
ADAPTIVE_RATE = True
BACKGROUND = (0, 0, 0)  # (31, 0, 10)  # (127, 0, 31)
POINTS = []
COLOURS = []
display_params = {'Width': WIDTH, 'Height': HEIGHT, 'Line width': LINE_WIDTH, 'Dynamic shading': DYNAMIC_SHADING,
                  'Colouring scheme': COLOURING_SCHEME_TYPE}
"""
    the whole class of curves that this program is able to display can be decomposed into three components:
        the base curve,
        a spirograph-like curling component which results in a curls-like band in place of the sole line of the base curve
        and a radius curve which adds big waves to the now band-like line of the curve
    t will denote the measure of rotation vs time
    Let's take a closer look:
        (B) the base curve (lissajous or some other type): (b_x(t), b_y(t)) e.g. (cos(t), sin(t)), or (2cos(t), sin(2t)), etc,
        (C) the curls: (c_x(t), c_y(t)) e.g. (cos(s*t), sin(s*t)) where s expresses the difference in the rotational speeds
            of the base curve and the curls-curve,
        (R) the radius curve is either a factor of the linear combination of the other two:
          R(t) = R_0 (C r(q t) + 1 - C) where c in [0, 1] expresses the strength of the waving effect, i.e. when C = 0,
            R(t) is simply R_0. E.g. r(q t + b) = sin(q t + b) or r(q t + b) = 4 min((q t + b) % 1, (-(q t + b)) % 1) - 1,
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
base_x = 'cos'
base_y = 'sin'
curls_x = 'cos'
curls_y = 'sin'
rad_f = 'zin'
ORTHOGONAL_WAVES = True
NORMALISE_WAVES = False
f = {'base_x': base_x, 'base_y': base_y, 'curls_x': curls_x, 'curls_y': curls_y, 'rad_f': rad_f,
     'Rad shift': ORTHOGONAL_WAVES, 'Normalise waves': NORMALISE_WAVES}
rad_ratio = 6 # 12
speed = 5.2  # 7.12  # 20.05
outer_params = {'R div r': rad_ratio, 'speed': speed}  # , 'C': C, 'q': q}
q = 0  # 20
C = 0.85  # 0.85
radius_curve_coeffs = {'C': C, 'q': q, 'b': 0}  # np.pi / 2}
base_a = 1  # 4
base_b = 0  # np.pi / 2
base_c = 2  # 3
base_A, base_B = 2, 1
base_curve_coeffs = {'A': base_A, 'a': base_a, 'b': base_b, 'B': base_B, 'c': base_c, 'd': 0}
curls_curve_coeffs = {'A': 1, 'a': 1, 'b': 0, 'B': 1, 'c': 1, 'd': 0}
curves = [radius_curve_coeffs, base_curve_coeffs, curls_curve_coeffs]
curve_codes = ['r', 'b', 'c']
params = {(key + (('_' + curve_codes[i]) if key in 'ABabcd' else '')): curves[i][key] for i in range(len(curve_codes))
          for key in curves[i].keys()}
print(params.keys())
defaults = {key: 0 if key[0] == 'b' else 1 for key in params.keys()}
defaults['q'] = 1
defaults['speed'] = 1
defaults['R div r'] = 0
defaults['C'] = 1


def get_name2():
    name = ''
    for key, val in outer_params.items():
        name += f'{key} = {val}, '
    for i in range(len(curves)):
        curve = curves[i]
        for key, val in curve.items():
            key += (('_' + curve_codes[i]) if key in 'ABabcd' else '')
            if val != defaults[key]:
                name += key + (' = {' + (':.2f' if val % 1 > 0.01 else '') + '}').format(val) + ', '
    name = name[:-2]
    return name


def get_name(R=900):
    operand_defaults = {'': 1, '*': 1, '/': 1, '+': 0, '-': 0, '(': '', ')': ''}

    def format_for_print(a):
        if type(a) == type(''):
            return a
        if a == round(a):
            return round(a)
        return a if len(str(a)) <= 5 else round(a, 3)

    def get_str_expr(literals):
        operands = ['', '(', '', ' + ', ')']
        st = ''
        if literals[0] != operand_defaults[operands[0]]:
            st = str(format_for_print(literals[0])) + operands[0]
        st += str(literals[1]) + operands[1]
        if literals[2] != operand_defaults[operands[2]]:
            st += str(format_for_print(literals[2])) + operands[2]
        st += str(literals[3])
        if literals[4] != operand_defaults[operands[3].strip()]:
            st += operands[3] + str(format_for_print(literals[4]))
        st += operands[-1]
        return st

    base_x_str = get_str_expr([base_curve_coeffs['A'], base_x, base_curve_coeffs['a'], 't', base_curve_coeffs['b']])
    base_y_str = get_str_expr([base_curve_coeffs['B'], base_y, base_curve_coeffs['c'], 't', base_curve_coeffs['d']])
    curls_x_str = get_str_expr(
        [curls_curve_coeffs['A'], curls_x, curls_curve_coeffs['a'] * speed, 't', curls_curve_coeffs['b']])
    curls_y_str = get_str_expr(
        [curls_curve_coeffs['B'], curls_y, curls_curve_coeffs['c'] * speed, 't', curls_curve_coeffs['d']])
    x_str = base_x_str + (' + ' if curls_x in ['cos', 'coz'] else ' - ') + curls_x_str
    y_str = base_y_str + (' + ' if curls_y in ['cos', 'coz'] else ' - ') + curls_y_str

    if ORTHOGONAL_WAVES:
        name = ' -- R(t, x(t), y(t)) = R(t)(x(t) + r_x(t), y(t) + r_y(t))'
        rad_x_str = get_str_expr(
            [-(1 - C) / 3 * base_curve_coeffs['A'] * base_curve_coeffs['a'] ** 2, base_x, base_curve_coeffs['a'], 't',
             base_curve_coeffs['b']])
        rad_x_str = ('normed({})' if NORMALISE_WAVES else '{}').format(get_str_expr(
            [rad_x_str, rad_f, q, 't', radius_curve_coeffs['b']]))
        rad_y_str = get_str_expr(
            [-(1 - C) / 3 * base_curve_coeffs['B'] * base_curve_coeffs['c'] ** 2, base_y, base_curve_coeffs['c'], 't',
             base_curve_coeffs['d']])
        rad_y_str = ('normed({})' if NORMALISE_WAVES else '{}').format(
            get_str_expr([rad_y_str, rad_f, q, 't', radius_curve_coeffs['b']]))
        # + (' div sqrt(square(d_2 base_x) + square(d_2 base_y))' if NORMALISE_WAVES else '')
        x_str += ' + ' + rad_x_str
        y_str += ' + ' + rad_y_str
        rad_f_str = str(round(R))

    else:
        name = ' -- R(t, x(t), y(t)) = R(t)(x(t), y(t))'
        rad_f_str = get_str_expr([round(R), rad_f, q, radius_curve_coeffs['b']])
    name = f'{rad_f_str}({x_str}, {y_str})' + name
    return name


def get_colour(spirog, colour=np.array([255, 127, 0])):
    cx, cy = COLOURING_SCHEME_TYPE + 'x', COLOURING_SCHEME_TYPE + 'y'
    if MY_COLOUR_SCHEME:
        dx, dy = spirog.get_derivatives(x=cx, y=cy)
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
        dx, dy = spirog.get_derivatives(x=cx, y=cy)
        d = (dx ** 2 + dy ** 2) ** 0.5
        d = (d / max([d, spirog.get_max_diff(x=cx, y=cy) * 0.9])) ** 1
        # print(d)
        strength = 0.6
        colour = np.round(strength * (1 / strength - (1 - d)) * colour).astype(int)
    if np.any(colour < 0) or np.any(colour > 255):
        colour = (255, 255, 255)
    return tuple(colour)


def main():
    pg.init()
    pg.font.init()
    global base_curve_coeffs, curls_curve_coeffs, radius_curve_coeffs
    spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
                       base_curve=base_curve_coeffs, curls=curls_curve_coeffs, rad_curve=radius_curve_coeffs,
                       rad_f=rad_f, base_f=(base_x, base_y), curls_f=(curls_x, curls_y),
                       ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES)
    draw = Draw(width=WIDTH, height=HEIGHT, DISPLAY=True, SAVE_IMAGE=True, BACKGROUND=BACKGROUND, LINE_WIDTH=2,
                name=get_name(spiro.R0))
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
                draw.screen.fill(BACKGROUND)
                # screen.fill((0, 0, 0))
                # screen.blit(pygame.transform.scale(pic, screen.get_size()), (0, 0))
                # pygame.display.update()
                pg.display.update()
                pass

        x0, y0 = x, y
        x, y = spiro.update()
        POINTS += [(x, y)]
        colour = get_colour(spiro)
        COLOURS += [colour]
        draw.draw_window(x0, y0, x, y, colour=colour)
        pygame_widgets.update(events)
    pg.quit()
    draw.save(name=get_name(spiro.R0), final_save=True)


if __name__ == '__main__':
    main()
