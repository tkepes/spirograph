from utils import least_multiple

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

from dataclasses import dataclass
from numpy import pi as pi


@dataclass
class Params:
    WIN: None
    WIDTH: int = 500
    HEIGHT: int = 400
    BACKGROUND: tuple = (255, 255, 255)
    SPF: int = 10
    N: int = 50
    ALPHA: float = 0.0
    BETA: float = 1.0
    GAMMA: float = 0.0


SPF = 100  # steps per frame
FPS = 20
WIDTH, HEIGHT = 2000, 2000
LINE_WIDTH = 1
DYNAMIC_SHADING = True
MY_COLOUR_SCHEME = True
COLOURING_SCHEME_BASE: str = '(base+curls)_'
COLOURING_SCHEME_BASE_choices = ['curls_', 'base_', 'rad_', '(base+curls)_', '(base+rad)_']
# '' for the whole curve, 'curls_' for curls, 'base_' for base, 'rad_' for the radius,
# '(base+curls)_' for the whole curve without the radius, '(base+rad)_' for the whole curve without the curls
BIPOLAR_COLOUR_SCHEME = False
ADAPTIVE_RATE = True
BACKGROUND = (0, 0, 0)  # (31, 0, 10)  # (127, 0, 31)
POINTS = []
COLOURS = []
draw_rate = 1.0
display_params = {'Width': WIDTH, 'Height': HEIGHT, 'Line width': LINE_WIDTH, 'Dynamic shading': DYNAMIC_SHADING,
                  'Colouring scheme': COLOURING_SCHEME_BASE, '': BIPOLAR_COLOUR_SCHEME,
                  'Use adaptive draw_rate': ADAPTIVE_RATE, 'draw_rate ': draw_rate}
base_x = 'cos'
base_y = 'sin'
curls_x = 'cos'
curls_y = 'sin'
rad_f = 'sin'
rad_x, rad_y = 'dy', 'dx'
rad_A, rad_B = -1, 1
rad_xy_coeffs = {'A': rad_A, 'a': 1, 'b': 0.0, 'B': rad_B, 'c': 1, 'd': 0.0}
ORTHOGONAL_WAVES = True
NORMALISE_WAVES = False
f = {'base_x': base_x, 'base_y': base_y, 'curls_x': curls_x, 'curls_y': curls_y, 'rad_f': rad_f,
     'Rad shift': ORTHOGONAL_WAVES, 'Normalise waves': NORMALISE_WAVES}
base_a = 1  # 4
base_b = 0.0
base_c = 2
base_A, base_B = 2, 1
base_curve_coeffs = {'A': base_A, 'a': base_a, 'b': base_b, 'B': base_B, 'c': base_c, 'd': 0.0}
lm = least_multiple(base_a, base_c)
rad_ratio, speed = 1 * 2 * (base_a + base_c), 3 * min((base_a + base_c), lm) + 0.12
# rad_ratio = 12  # 12
# speed = 12.05  # 7.12  # 20.05
base_a = 5  # 4
base_b = pi / 2
base_c = 4  # 3
base_A, base_B = 1, 1
base_curve_coeffs = {'A': base_A, 'a': base_a, 'b': base_b, 'B': base_B, 'c': base_c, 'd': 0.0}
lm = least_multiple(base_a, base_c)
rad_ratio, speed = 1 * 2 * (base_a + base_c), 3 * min((base_a + base_c), lm) + 0.12
# speed = 150.05
outer_params = {'R div r': rad_ratio, 'speed': speed}  # , 'C': C, 'q': q}
q = 0.0  # 20
C = 0.5  # 0.85
radius_curve_coeffs = {'C': C, 'q': q, 'b': 0.0}  # np.pi / 2}
curls_A, curs_B = 1, 1
curls_curve_coeffs = {'A': curls_A, 'a': 1, 'b': 0.0, 'B': curs_B, 'c': 1, 'd': 0.0}
curves = [radius_curve_coeffs, base_curve_coeffs, curls_curve_coeffs]
if ORTHOGONAL_WAVES:
    curve_codes = ['r', 'b', 'c']  # curve_codes = ['r_xy', 'r', 'b', 'c']
else:
    curve_codes = ['r', 'b', 'c']
formula_params = {key + (('_' + curve_codes[i]) if key in 'ABabcd' else ''): curves[i][key] for i in
                  range(len(curve_codes)) for key in curves[i].keys()}
defaults = {key: 0 if key[0] in 'bd' else 1 for key in formula_params.keys()}
defaults['q'] = 0.0
defaults['speed'] = 1.0
defaults['R div r'] = -1
defaults['C'] = 1.0

# streamlit stuff
slider_keys = list(set(key for i in range(len(curve_codes)) for key in curves[i].keys())) + list(outer_params.keys()) # _{curve_codes[i]}
widget_types = ['slider', 'checkbox', 'selectbox']
widget_type_of = {param: 'slider' for param in slider_keys}
func_names = ['sin', 'cos', 'zin', 'coz']

slider_min = {key: 0.0 if key in 'bdqspeedC' else 0 for key in slider_keys}
slider_min['R div r'] = 1
slider_step = {key: 1 if key in 'ABac' else (0.1 * pi if key in 'bd' else 0.01) for key in slider_keys}
slider_step['R div r'] = 1
slider_max = {key: 20 if key in 'ABac' else (2 * pi if key in 'bd' else 200.0) for key in slider_keys}
slider_max['R div r'] = 30
slider_max['C'] = 1.0


# base curve choices

def get_name2(outer_params=outer_params, curves=curves, curve_codes=curve_codes, defaults=defaults):
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


def get_name(R=900, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x, curls_y=curls_y,
             curls_curve_coeffs=curls_curve_coeffs, radius_curve_coeffs=radius_curve_coeffs, speed=speed, q=q,
             rad_f=rad_f):
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
        rad_f_str = ''  # str(round(R))

    else:
        name = ' -- R(t, x(t), y(t)) = R(t)(x(t), y(t))'
        rad_f_str = get_str_expr([round(R), rad_f, q, radius_curve_coeffs['b']])
    name = f'{rad_f_str}({x_str}, {y_str})' + name
    while '+ -' in name:
        name = name.replace('+ -', '- ')
    while '  ' in name:
        name = name.replace('  ', ' ')
    return name
