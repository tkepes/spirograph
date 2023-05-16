import numpy as np
# import sys
# sys.path.insert(0, '.')
import streamlit as st
from Image import MyImage
from Spirograph import Spirograph, pi
from Parameters import *
from Colours import *
from utils import least_multiple

curve_codes = ['outer', 'b', 'c', 'r']
curves = [outer_params, base_curve_coeffs, curls_curve_coeffs, radius_curve_coeffs]
base_choices = ['', 'circle', 'lissajous(1, 2)', 'lissajous(3, 2)', 'lissajous(4, 3)', 'lissajous(5, 4)',
                'lissajous(6, 5)']

with st.sidebar.expander("Base curve settings") as exp1:
    base_choice = st.selectbox('base choice', base_choices, index=0)
    if 'lissajous' in base_choice:
        base_x_ind, base_y_ind = 1, 0
        a, c = int(base_choice[-5]), int(base_choice[-2])
        A, b = 1, 0.0
        if (a, c) == (1, 2):
            A = 2
        else:
            b = np.pi / 2
        base_curve_coeffs = {'A': A, 'a': a, 'b': b, 'B': 1, 'c': c, 'd': 0.0}
    elif 'circle' in base_choice:
        base_x_ind, base_y_ind = 1, 0
        base_curve_coeffs = {'A': 1, 'a': 1, 'b': 0.0, 'B': 1, 'c': 1, 'd': 0.0}
    else:
        base_x_ind, base_y_ind = 1, 0
        base_curve_coeffs = {'A': 1, 'a': 1, 'b': 0.0, 'B': 1, 'c': 1, 'd': 0.0}

    base_x = st.selectbox('base_x', func_names, index=base_x_ind)
    base_y = st.selectbox('base_y', func_names, index=base_y_ind)
    for param in base_curve_coeffs:
        base_curve_coeffs[param] = st.slider(param + ('_b' if param in 'ABabcd' else ''), min_value=slider_min[param],
                                             value=base_curve_coeffs[param], max_value=slider_max[param],
                                             step=slider_step[param])

with st.sidebar.expander("Curls curve settings"):
    curls_choices = base_choices
    curls_choice = st.selectbox('curls choices', curls_choices, index=0)
    if 'lissajous' in curls_choice:
        curls_x_ind, curls_y_ind = 1, 0
        a, c = int(curls_choice[-5]), int(curls_choice[-2])
        lm = least_multiple(a, c)
        rad_ratio, speed = 2 * lm, 3 * lm + 0.12
        # if (a, c) == (1, 2):
        #     rad_ratio, speed = 4, 7.12
        #     # rad_ratio, speed = 4, 1.04
        # elif (a, c) == (3, 2):
        #     rad_ratio, speed = 12, 12.05
        # elif (a, c) == (4, 3):
        #     rad_ratio, speed = 12, 12.05
        # else:
        #     rad_ratio, speed = 8, 20.24
    elif 'circle' in curls_choice:
        rad_ratio, speed = 2, 1.04
        curls_x_ind, curls_y_ind = 1, 0
    else:
        curls_x_ind, curls_y_ind = 1, 0
    outer_params = {'R div r': rad_ratio, 'speed': speed}

    curls_x = st.selectbox('curls_x', func_names, index=curls_x_ind)
    curls_y = st.selectbox('curls_y', func_names, index=curls_y_ind)
    for param in curls_curve_coeffs:
        curls_curve_coeffs[param] = st.slider(param + ('_c' if param in 'ABabcd' else ''), min_value=slider_min[param],
                                              value=curls_curve_coeffs[param], max_value=slider_max[param],
                                              step=slider_step[param])

for i in range(len(curves)):
    curve = curves[i]
    if curve_codes[i] in 'bc':
        continue
    for param in curve:
        curve[param] = st.sidebar.slider(param + (('_' + curve_codes[i]) if param in 'ABabcd' else ''),
                                         value=curve[param], min_value=slider_min[param], max_value=slider_max[param],
                                         step=slider_step[param])

spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
                   base_curve=base_curve_coeffs, curls=curls_curve_coeffs, rad_curve=radius_curve_coeffs,
                   rad_f=rad_f, base_f=(base_x, base_y), curls_f=(curls_x, curls_y),
                   ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES)
name = get_name(spiro.R0, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x,
                curls_y=curls_y, curls_curve_coeffs=curls_curve_coeffs, radius_curve_coeffs=radius_curve_coeffs,
                speed=speed, q=q, rad_f=rad_f)
draw = MyImage(width=WIDTH, height=HEIGHT, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH, name=name, st_res=1000)
# DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
x, y = spiro.update()
run = True
image_holder = st.empty()
image_holder.image(draw.st_im)
st.button('Save now!', 'save', on_click=lambda: draw.save(final_save=False))
i = 0
while spiro.t < spiro.per * pi:
    x0, y0 = x, y
    x, y = spiro.update()
    colour = get_colour(spiro, colouring_scheme_type=COLOURING_SCHEME_BASE, my_colour_scheme=MY_COLOUR_SCHEME,
                        bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME, dynamic_shading=DYNAMIC_SHADING)
    draw.line(x0, y0, x, y, colour=colour, width=LINE_WIDTH)
    if i % SPF == 0:
        image_holder.image(draw.st_im)
    i += 1
image_holder.image(draw.st_im)
name = get_name(spiro.R0, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x,
                curls_y=curls_y, curls_curve_coeffs=curls_curve_coeffs, radius_curve_coeffs=radius_curve_coeffs,
                speed=speed, q=q, rad_f=rad_f)
draw.save(name=name, final_save=True)
