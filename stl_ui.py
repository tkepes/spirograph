import numpy as np
import sys

sys.path.insert(0, '.')
import streamlit as st
from Image import MyImage
from Spirograph import Spirograph
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
    R(t)(x(t), y(t))
    where (x(t), y(t)) = (x0(t) + r/R * x1(t), y0(t) + r/R * y1(t))
    and (x0(t), y0(t)) = (A_0 cos(a_0t + b_0), B_0 sin(c_0t + d_0))
    and (x1(t), y1(t)) = (A_1 cos(a_1t + b_1), B_1 sin(c_1t + d_1))
    and R(t) = R((1 - C)sin(qt + b) + C)
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

for i in range(len(curves)):
    curve = curves[i]
    for param in curve:
        print(param)
        curve[param] = st.sidebar.slider(((curve_codes[i] + '_') if param in 'ABabcd' else '') + param,
                                         value=curve[param])


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


spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, base_curve=base_curve,
                   ribbon_curve=ribbon_curve, radius_curve=radius_curve, rad_type='', ORTHOGONAL_WAVES=True)
draw = MyImage(width=WIDTH, height=HEIGHT, BACKGROUND=BACKGROUND, LINE_WIDTH=2, name=get_name(), st_res=1000)
# DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
x, y = spiro.update()
run = True
image_holder = st.empty()
image_holder.image(draw.st_im)
st.button('Save now!', 'save', on_click=lambda: draw.save(final_save=False))
while run:
    x0, y0 = x, y
    x, y = spiro.update()
    colour = get_colour(spiro)
    draw.line(x0, y0, x, y, colour=colour, width=LINE_WIDTH)
    image_holder.image(draw.st_im)
draw.save(name=get_name(), final_save=True)
