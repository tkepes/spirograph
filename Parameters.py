from utils import least_multiple, get_period

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


class MyParams:
    def __init__(self, *args):
        self.SPF = 100  # steps per frame
        self.FPS = 20
        self.WIDTH, self.HEIGHT = 2000, 2000
        self.MARGIN = 20
        self.LINE_WIDTH = 2
        self.DYNAMIC_SHADING = True
        self.FLIP_DYNAMIC_SHADING = False
        self.MY_COLOUR_SCHEME = True
        self.COLOURING_SCHEME_BASE: str = '(base+curls)_'
        self.COLOURING_SCHEME_BASE_choices = ['curls_', 'base_', 'rad_', '(base+curls)_', '(base+rad)_']
        # '' for the whole curve, 'curls_' for curls, 'base_' for base, 'rad_' for the radius,
        # '(base+curls)_' for the whole curve without the radius, '(base+rad)_' for the whole curve without the curls
        self.BIPOLAR_COLOUR_SCHEME = False
        self.ADAPTIVE_RATE = True
        self.BACKGROUND = (0, 0, 0)
        self.sect_fact = 4
        self.draw_rate = 1000
        # self.display_params = {'Width': self.WIDTH, 'Height': self.HEIGHT, 'Line width': self.LINE_WIDTH,
        #                       'Dynamic shading': self.DYNAMIC_SHADING, 'Colouring scheme': self.COLOURING_SCHEME_BASE,
        #                       '': self.BIPOLAR_COLOUR_SCHEME, 'Use adaptive draw_rate': self.ADAPTIVE_RATE,
        #                       'draw_rate ': self.draw_rate, 'FPS': self.FPS, 'SPF': self.SPF}
        self.base_x = 'cos'
        self.base_y = 'sin'
        self.curls_x = 'cos'
        self.curls_y = 'sin'
        self.rad_f = 'sin'
        self.rad_x, self.rad_y = 'dbase_y', 'dbase_x'
        self.rad_A, self.rad_B = -1, 1
        self.rad_xy_coeffs = {'A': self.rad_A, 'a': 1, 'b': 0., 'B': self.rad_B, 'c': 1, 'd': 0.}
        self.ORTHOGONAL_WAVES = True
        self.NORMALISE_WAVES = False
        # self.f = {'base_x': self.base_x, 'base_y': self.base_y, 'curls_x': self.curls_x, 'curls_y': self.curls_y,
        #           'rad_f': self.rad_f,
        #           'Rad shift': self.ORTHOGONAL_WAVES, 'Normalise waves': self.NORMALISE_WAVES}
        self.base_a = 1  # 4
        self.base_b = 0.
        self.base_c = 2
        self.base_A, self.base_B = 2, 1
        self.base_curve_coeffs = {'A': self.base_A, 'a': self.base_a, 'b': self.base_b, 'B': self.base_B,
                                  'c': self.base_c, 'd': 0.}
        self.base_per = get_period(self.base_a, self.base_c, 2)
        self.lm = least_multiple(self.base_a, self.base_c)
        self.speed = 7.12
        self.rad_ratio, self.speed = 1 * 2 * (self.base_a + self.base_c), round(
            self.base_per // 2 * (self.speed // 1) + self.speed % 1, 2)
        # self.rad_ratio = 12  # 12
        # self.speed = 12.05  # 7.12  # 20.05
        # self.base_a = 5  # 4
        # self.base_b = pi / 2
        # self.base_c = 4  # 3
        # self.base_A, self.base_B = 1, 1
        # self.base_curve_coeffs = {'A': self.base_A, 'a': self.base_a, 'b': self.base_b, 'B': self.base_B,
        #                           'c': self.base_c, 'd': 0.}
        # self.lm = least_multiple(self.base_a, self.base_c)
        # self.rad_ratio, self.speed = 1 * 2 * (self.base_a + self.base_c),
        # 3 * min((self.base_a + self.base_c), self.lm) + .12
        # self.speed = 150.05
        self.outer_params = {'R div r': self.rad_ratio, 'speed': self.speed}
        self.q = 0.  # 20
        self.C = .5  # .85
        self.radius_curve_coeffs = {'C': self.C, 'q': self.q, 'b': 0.}  # np.pi / 2}
        self.curls_A, self.curs_B = 1, 1
        self.curls_curve_coeffs = {'A': self.curls_A, 'a': 1, 'b': 0., 'B': self.curs_B, 'c': 1, 'd': 0.}
        self.curves = [self.radius_curve_coeffs, self.base_curve_coeffs, self.curls_curve_coeffs]
        if self.ORTHOGONAL_WAVES:
            self.curve_codes = ['r', 'b', 'c']  # curve_codes = ['r_xy', 'r', 'b', 'c']
        else:
            self.curve_codes = ['r', 'b', 'c']
        self.formula_params = {key + (('_' + self.curve_codes[i]) if key in 'ABabcd' else ''): self.curves[i][key] for i
                               in range(len(self.curve_codes)) for key in self.curves[i].keys()}
        self.defaults = {key: 0 if key[0] in 'bd' else 1 for key in self.formula_params.keys()}
        self.defaults['q'] = 0.
        self.defaults['speed'] = 1.
        self.defaults['R div r'] = -1
        self.defaults['C'] = 1.

        # streamlit stuff
        self.slider_keys = list(set(key for i in range(len(self.curve_codes)) for key in self.curves[i].keys())) + list(
            self.outer_params.keys())  # _{curve_codes[i]}
        self.widget_types = ['slider', 'checkbox', 'selectbox']
        self.widget_type_of = {param: 'slider' for param in self.slider_keys}
        self.func_names = ['sin', 'cos', 'zin', 'coz']

        self.slider_min = {key: 0. if key in 'bdqspeedC' else 0 for key in slider_keys}
        self.slider_min['R div r'] = 1
        self.slider_step = {key: 1 if key in 'ABac' else (.1 * pi if key in 'bd' else .01) for key in self.slider_keys}
        self.slider_step['R div r'] = 1
        self.slider_max = {key: 20 if key in 'ABac' else (2 * pi if key in 'bd' else 200.) for key in self.slider_keys}
        self.slider_max['R div r'] = 30
        self.slider_max['C'] = 1.

    def set_SPF(self, value):
        self.SPF = value

    def set_FPS(self, value):
        self.FPS = value

    def set_WIDTH(self, value):
        self.WIDTH = value

    def set_HEIGHT(self, value):
        self.HEIGHT = value

    def set_MARGIN(self, value):
        self.MARGIN = value

    def set_LINE_WIDTH(self, value):
        self.LINE_WIDTH = value

    def set_DYNAMIC_SHADING(self, value):
        self.DYNAMIC_SHADING = value

    def set_MY_COLOUR_SCHEME(self, value):
        self.MY_COLOUR_SCHEME = value

    def set_COLOURING_SCHEME_BASE(self, value):
        self.COLOURING_SCHEME_BASE = value

    def set_COLOURING_SCHEME_BASE_choices(self, value):
        self.COLOURING_SCHEME_BASE_choices = value

    def set_BIPOLAR_COLOUR_SCHEME(self, value):
        self.BIPOLAR_COLOUR_SCHEME = value

    def set_ADAPTIVE_RATE(self, value):
        self.ADAPTIVE_RATE = value

    def set_BACKGROUND(self, value):
        self.BACKGROUND = value

    def set_draw_rate(self, value):
        self.draw_rate = value

    def set_base_x(self, value):
        self.base_x = value

    def set_base_y(self, value):
        self.base_y = value

    def set_curls_x(self, value):
        self.curls_x = value

    def set_curls_y(self, value):
        self.curls_y = value

    def set_rad_f(self, value):
        self.rad_f = value

    def set_rad_x(self, value):
        self.rad_x = value

    def set_rad_y(self, value):
        self.rad_y = value

    def set_rad_A(self, value):
        self.rad_A = value

    def set_rad_B(self, value):
        self.rad_B = value

    def set_rad_xy_coeffs(self, value):
        self.rad_xy_coeffs = value

    def set_ORTHOGONAL_WAVES(self, value):
        self.ORTHOGONAL_WAVES = value

    def set_NORMALISE_WAVES(self, value):
        self.NORMALISE_WAVES = value

    def set_base_a(self, value):
        self.base_a = value

    def set_base_b(self, value):
        self.base_b = value

    def set_base_c(self, value):
        self.base_c = value

    def set_base_A(self, value):
        self.base_A = value

    def set_base_B(self, value):
        self.base_B = value

    def set_base_curve_coeffs(self, value):
        self.base_curve_coeffs = value

    def set_base_per(self, value):
        self.base_per = value

    def set_lm(self, value):
        self.lm = value

    def set_speed(self, value):
        self.speed = value

    def set_rad_ratio(self, value):
        self.rad_ratio = value

    def set_outer_params(self, value):
        self.outer_params = value

    def set_q(self, value):
        self.q = value

    def set_C(self, value):
        self.C = value

    def set_radius_curve_coeffs(self, value):
        self.radius_curve_coeffs = value

    def set_curls_A(self, value):
        self.curls_A = value

    def set_curs_B(self, value):
        self.curs_B = value

    def set_curls_curve_coeffs(self, value):
        self.curls_curve_coeffs = value

    def set_curves(self, value):
        self.curves = value

    def set_curve_codes(self, value):
        self.curve_codes = value

    def set_formula_params(self, value):
        self.formula_params = value

    def set_defaults(self, value):
        self.defaults = value

    def set_slider_keys(self, value):
        self.slider_keys = value

    def set_widget_types(self, value):
        self.widget_types = value

    def set_widget_type_of(self, value):
        self.widget_type_of = value

    def set_func_names(self, value):
        self.func_names = value

    def set_slider_min(self, value):
        self.slider_min = value

    def set_slider_step(self, value):
        self.slider_step = value

    def set_slider_max(self, value):
        self.slider_max = value


SPF = 100  # steps per frame
FPS = 20
WIDTH, HEIGHT = 2000, 2000
MARGIN = 50
LINE_WIDTH = 2
DYNAMIC_SHADING = True
FLIP_DYNAMIC_SHADING = False
strength = .3
MY_COLOUR_SCHEME = True
COLOURING_SCHEME_BASE: str = '(base+curls)_'
COLOURING_SCHEME_BASE_choices = ['curls_', 'base_', 'rad_', '(base+curls)_', '(base+rad)_']
# '' for the whole curve, 'curls_' for curls, 'base_' for base, 'rad_' for the radius,
# '(base+curls)_' for the whole curve without the radius, '(base+rad)_' for the whole curve without the curls
BIPOLAR_COLOUR_SCHEME = False
ADAPTIVE_RATE = True
BACKGROUND = (0, 0, 0)  # (31, 0, 10)  # (127, 0, 31)
sect_fact = 4
base_sect_fact = 4
base_rad_sect_fact = 4
POINTS = []
COLOURS = []
draw_rate = min(WIDTH, HEIGHT) // 20
display_params = {'Width': WIDTH, 'Height': HEIGHT, 'Line width': LINE_WIDTH, 'Dynamic shading': DYNAMIC_SHADING,
                  'Colouring scheme': COLOURING_SCHEME_BASE, '': BIPOLAR_COLOUR_SCHEME,
                  'Use adaptive draw_rate': ADAPTIVE_RATE, 'draw_rate ': draw_rate, 'FPS': FPS, 'SPF': SPF}
func_names = ['sin', 'cos', 'zin', 'coz']
coeff_names = ['A', 'B', 'a', 'c', 'b', 'd']
coeff_labels = {key: key for key in coeff_names}
coeff_labels['b'] = 'b'
coeff_labels['d'] = 'd'
col_setter = lambda text, col='red': f':{col}[{text}]'
my_cols = {'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'black': (0, 0, 0),
           'white': (255, 255, 255)}
coeff_cols = {**{par: 'blue' for par in 'AB'}, **{par: 'red' for par in 'ac'},
              **{par: 'green' for par in 'bd'}, **{par: 'orange' for par in func_names}}
# coeff_cols = {**{par: my_cols['blue'] for par in 'AB'}, **{par: my_cols['red'] for par in 'ac'},
#               **{par: my_cols['green'] for par in 'bd'}, **{par: my_cols['yellow'] for par in func_names}}
# par_cols = {**{par: lambda text: col_setter(text, col=str(coeff_cols[par])) for par in coeff_names},
#             **{par: lambda text: col_setter(text, col=coeff_cols[par]) for par in func_names}}
par_cols = {par: lambda text: col_setter(text, col=coeff_cols[par]) for par in func_names}
par_cols['A'] = lambda text: col_setter(text, col='blue')
par_cols['B'] = lambda text: col_setter(text, col='blue')
par_cols['a'] = lambda text: col_setter(text, col='red')
par_cols['c'] = lambda text: col_setter(text, col='red')
par_cols['b'] = lambda text: col_setter(text, col=coeff_cols['b'])
par_cols['d'] = lambda text: col_setter(text, col=coeff_cols['d'])
curve_cols = {'base': 'red', 'curls': 'blue', 'rad': 'green'}
test_line_lengths=False
curvature_test=False
base_x = 'cos'
base_y = 'sin'
curls_x = 'cos'
curls_y = 'sin'
rad_f = 'sin'
rad_x, rad_y = 'dbase_y', 'dbase_x'
rad_A, rad_B = -1, 1
rad_xy_coeffs = {'A': rad_A, 'a': 1, 'b': 0., 'B': rad_B, 'c': 1, 'd': 0.}
ORTHOGONAL_WAVES = True
NORMALISE_WAVES = False
f = {'base_x': base_x, 'base_y': base_y, 'curls_x': curls_x, 'curls_y': curls_y, 'rad_f': rad_f,
     'Rad shift': ORTHOGONAL_WAVES, 'Normalise waves': NORMALISE_WAVES}
base_a = 1  # 4
base_b = 0.
base_c = 2
base_A, base_B = 2, 1
base_curve_coeffs = {'A': base_A, 'a': base_a, 'b': base_b, 'B': base_B, 'c': base_c, 'd': 0.}
base_per = get_period(base_a, base_c, 2)
lm = least_multiple(base_a, base_c)
speed = 7.12
rad_ratio, speed = 1 * 2 * (base_a + base_c), round(base_per // 2 * (speed // 1) + speed % 1, 2)
# rad_ratio = 12  # 12
# speed = 12.05  # 7.12  # 20.05
# base_a = 5  # 4
# base_b = pi / 2
# base_c = 4  # 3
# base_A, base_B = 1, 1
# base_curve_coeffs = {'A': base_A, 'a': base_a, 'b': base_b, 'B': base_B, 'c': base_c, 'd': 0.}
# lm = least_multiple(base_a, base_c)
# rad_ratio, speed = 1 * 2 * (base_a + base_c), 3 * min((base_a + base_c), lm) + .12
# speed = 150.05
outer_params = {'R div r': rad_ratio, 'speed': speed}  # , 'C': C, 'q': q}
q = 0  # 20
C = .5  # .85
radius_curve_coeffs = {'C': C, 'q': q, 'b': 0.}  # np.pi / 2}
curls_A, curs_B = 1, 1
curls_curve_coeffs = {'A': curls_A, 'a': 1, 'b': 0., 'B': curs_B, 'c': 1, 'd': 0.}
curves = [radius_curve_coeffs, base_curve_coeffs, curls_curve_coeffs]
if ORTHOGONAL_WAVES:
    curve_codes = ['r', 'b', 'c']  # curve_codes = ['r_xy', 'r', 'b', 'c']
else:
    curve_codes = ['r', 'b', 'c']
formula_params = {key + (('_' + curve_codes[i]) if key in 'ABabcd' else ''): curves[i][key] for i in
                  range(len(curve_codes)) for key in curves[i].keys()}
defaults = {key: 0 if key[0] in 'bd' else 1 for key in formula_params.keys()}
defaults['q'] = 0.
defaults['speed'] = 1.
defaults['R div r'] = -1
defaults['C'] = 1.

# streamlit stuff
slider_keys = list(set(key for i in range(len(curve_codes)) for key in curves[i].keys())) + list(
    outer_params.keys())  # _{curve_codes[i]}
widget_types = ['slider', 'checkbox', 'selectbox']
widget_type_of = {param: 'slider' for param in slider_keys}

slider_min = {key: 0. if key in 'bdqspeedC' else 0 for key in slider_keys}
slider_min['R div r'] = 1
slider_step = {key: 1 if key in 'ABac' else (.1 * pi if key in 'bd' else .01) for key in slider_keys}
slider_step['R div r'] = 1
slider_max = {key: 20 if key in 'ABac' else (2 * pi if key in 'bd' else 200.) for key in slider_keys}
slider_max['R div r'] = 30
slider_max['C'] = 1.


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
                name += key + (' = {' + (':.2f' if val % 1 > .01 else '') + '}').format(val) + ', '
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


def get_name_1(R=900, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x,
               curls_y=curls_y,
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

    def str_mult(a, b, prod_char=' \cdot '):
        if 0 in [a, b]:
            return 0
        elif b == 1:
            return a
        elif a == 1:
            return b
        return f'{a}{prod_char}{b}'

    def str_add(a, b):
        if b == 0:
            return a
        elif a == 0:
            return b
        elif type(b) != type('') and b < 0:
            return f'{a} - {-b}'
        return f'{a} + {b}'

    def func_val_calc(coeffs, A='A', a='a', b='b', ff=base_x):
        t, pi_str = 't', 'pi'
        empty = ''
        return f'{str_mult(coeffs[A], f"{ff}({str_add(str_mult(coeffs[a], t), str_mult(round(coeffs[b] / pi, 2), pi_str, prod_char=empty))})", prod_char=empty)}'

    # base_x_str = str_mult(base_curve_coeffs['A'], base_x + '('+ str_add(str_mult(base_curve_coeffs['a'], 't'), base_curve_coeffs['b'])+')')

    base_x_str = func_val_calc(base_curve_coeffs, ff=base_x)
    base_y_str = func_val_calc(base_curve_coeffs, A='B', a='c', b='d', ff=base_y)
    curls_x_str = func_val_calc(curls_curve_coeffs, ff=curls_x)
    curls_y_str = func_val_calc(curls_curve_coeffs, A='B', a='c', b='d', ff=curls_y)
    curls_x_str = str_mult(1 / rad_ratio, curls_x_str, prod_char=' * ')
    curls_y_str = str_mult(1 / rad_ratio, curls_y_str, prod_char=' * ')
    x_str = base_x_str + (' + ' if curls_x in ['cos', 'coz'] else ' - ') + curls_x_str
    y_str = base_y_str + (' + ' if curls_y in ['cos', 'coz'] else ' - ') + curls_y_str

    if ORTHOGONAL_WAVES:
        name = ' -- R(t, x(t), y(t)) = R(t)(x(t) + r_x(t), y(t) + r_y(t))'
        my_coeffs = {key: base_curve_coeffs[key] for key in base_curve_coeffs.keys()}
        my_coeffs['A'] = -(1 - C) / 3 * base_curve_coeffs['A'] * base_curve_coeffs['a'] ** 2
        my_coeffs['B'] = -(1 - C) / 3 * base_curve_coeffs['B'] * base_curve_coeffs['c'] ** 2
        my_coeffs['q'] = q
        my_coeffs['rx'] = func_val_calc(my_coeffs, ff=base_x)
        my_coeffs['ry'] = func_val_calc(my_coeffs, A='B', a='c', b='d', ff=base_y)
        rad_x_str = ('normed({})' if NORMALISE_WAVES else '{}').format(
            func_val_calc(my_coeffs, A='rx', a='q', b='b', ff=rad_f))
        rad_y_str = ('normed({})' if NORMALISE_WAVES else '{}').format(
            func_val_calc(my_coeffs, A='ry', a='q', b='b', ff=rad_f))
        # + (' div sqrt(square(d_2 base_x) + square(d_2 base_y))' if NORMALISE_WAVES else '')
        x_str += (' + ' + rad_x_str if my_coeffs['A'] > 0 else ' - ' + rad_x_str[1:])
        y_str += (' + ' + rad_y_str if my_coeffs['B'] > 0 else ' - ' + rad_y_str[1:])
        rad_f_str = ''  # str(round(R))
    else:
        name = ' -- R(t, x(t), y(t)) = R(t)(x(t), y(t))'
        my_coeffs = {'A': (1 - C), 'q': q, 'b': radius_curve_coeffs['b']}
        rad_f_str = f'({str_add(func_val_calc(my_coeffs, a="q", ff=rad_f), C)})'
        # str_mult(round(R),  f'({str_add(func_val_calc(my_coeffs, a="q", ff=rad_f), C)})')
    name = f'{rad_f_str}({x_str}, {y_str})' + name
    while '+ -' in name:
        name = name.replace('+ -', '- ')
    while '  ' in name:
        name = name.replace('  ', ' ')
    return name
