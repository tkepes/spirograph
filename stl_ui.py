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


def get_base_image():
    w, h = 300, 300
    base_spiro = Spirograph(width=w, height=h, ADAPTIVE_RATE=ADAPTIVE_RATE, base_curve=base_curve_coeffs,
                            base_f=(base_x, base_y), section_fact=4)
    base_draw = MyImage(width=w, height=h, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH)
    x, y = base_spiro.get_point()
    while base_spiro.t < base_spiro.per * pi + 0.1:
        x0, y0 = x, y
        x, y = base_spiro.update(draw_rate=draw_rate / 2)
        colour = get_colour(base_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, dynamic_shading=DYNAMIC_SHADING,
                            my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME)
        base_draw.line(x0, y0, x, y, colour=colour, width=3)
    r = 2
    for n in range(4 * base_spiro.per):
        x, y = base_spiro.get_point(t=n * pi / base_spiro.per / 2)
        leftUpPoint = (x - r, y - r)
        rightDownPoint = (x + r, y + r)
        twoPointList = [leftUpPoint, rightDownPoint]
        base_draw.draw.ellipse(twoPointList, fill=(255, 255, 255))
    return base_draw.im


def get_curls_image():
    base_per = least_multiple(least_multiple(base_curve_coeffs['a'], base_curve_coeffs['c']), 2)
    w, h = 1000, 1000
    # print(f'base period: {base_per}, old speed {speed}, new speed: {(speed // 1) // base_per + speed % 1}')
    # , {round((speed // 1) // base_per + speed % 1, 2)}')
    curls_outer_params = {'R div r': outer_params['R div r'], 'speed': round((speed // 1) // base_per + speed % 1, 2)}
    curls_spiro = Spirograph(width=w, height=h, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=curls_outer_params,
                             curls=curls_curve_coeffs, curls_f=(curls_x, curls_y), section_fact=4)
    curls_draw = MyImage(width=w, height=h, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH)
    x, y = curls_spiro.get_point()
    while curls_spiro.t < curls_spiro.per * pi + 0.1:
        x0, y0 = x, y
        x, y = curls_spiro.update(draw_rate=draw_rate / 2)
        colour = get_colour(curls_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, dynamic_shading=DYNAMIC_SHADING,
                            my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME)
        curls_draw.line(x0, y0, x, y, colour=colour, width=1)
    print(f'curls_spiro.t = {curls_spiro.t}')
    return curls_draw.im


def get_curls_image_closeup():
    base_per = least_multiple(least_multiple(base_curve_coeffs['a'], base_curve_coeffs['c']), 2)
    base_per *= max(base_curve_coeffs['a'], base_curve_coeffs['c'])
    w_s, h_s = WIDTH, HEIGHT
    curls_outer_params = {'R div r': outer_params['R div r'],
                          'speed': round((2 * speed // 1) // base_per + speed % 1, 2)}
    curls_spiro = Spirograph(width=w_s, height=h_s, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=curls_outer_params,
                             curls=curls_curve_coeffs, curls_f=(curls_x, curls_y), section_fact=4)

    w = h = round(3 * curls_spiro.R0 / outer_params['R div r'])
    line_width = max(round(w_s // w * LINE_WIDTH), 1)
    print(f'width = {w}, width ratio = {w_s / w:.2f}, line width = {line_width}')
    curls_draw = MyImage(width=w, height=h, BACKGROUND=BACKGROUND, LINE_WIDTH=line_width)

    def shift(x, y):
        return x, max(0, y - (h_s - h) // 2)

    def IsOnImage(t=0):
        x, y = curls_spiro.get_point(t=t)
        x, y = shift(x, y)
        return 0 <= x < w and 0 <= y < h

    t_0 = pi
    for _ in range(curls_spiro.per // 2):
        t = t_0
        while IsOnImage(t):
            t -= 0.01
        curls_spiro.t = t
        while not IsOnImage(curls_spiro.t):
            # x0, y0 = x, y # x, y =
            curls_spiro.update(draw_rate=draw_rate / 2)
        x, y = curls_spiro.get_point()
        while IsOnImage(curls_spiro.t):
            x0, y0 = x, y
            x, y = curls_spiro.update(draw_rate=draw_rate / 2)
            colour = get_colour(curls_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, dynamic_shading=DYNAMIC_SHADING,
                                my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME)
            x0_d, y0_d = shift(x0, y0)
            x_d, y_d = shift(x, y)
            curls_draw.line(x0_d, y0_d, x_d, y_d, colour=colour)
        t_0 += 2 * pi
    return curls_draw.im


with st.sidebar.expander('Display settings') as disp:
    st.text('Image settings')  # with st.sidebar.expander("Image settings"):
    WIDTH = st.slider('Image width', value=WIDTH, min_value=0, max_value=10000)
    HEIGHT = st.slider('Image height', value=HEIGHT, min_value=0, max_value=10000)
    st.text('Display settings')
    LINE_WIDTH = st.slider('Curve width', value=LINE_WIDTH, min_value=1, max_value=20)
    DYNAMIC_SHADING = st.checkbox(label='Use dynamic shading?', value=DYNAMIC_SHADING)
    col_ind = 0
    if MY_COLOUR_SCHEME:
        col_ind = 1
    elif BIPOLAR_COLOUR_SCHEME:
        col_ind = 2
    colouring_choice = st.selectbox(label='colouring', options=['mono', 'multi', 'bipolar'], index=col_ind)
    MY_COLOUR_SCHEME = colouring_choice == 'multi'
    BIPOLAR_COLOUR_SCHEME = colouring_choice == 'bipolar'
    if MY_COLOUR_SCHEME:
        COLOURING_SCHEME_BASE = st.selectbox(label='colourin based on the derivatives:',
                                             options=[choice[:-1] for choice in COLOURING_SCHEME_BASE_choices],
                                             index=COLOURING_SCHEME_BASE_choices.index(COLOURING_SCHEME_BASE)) + '_'

    st.text('Drawing rate settings')  # with disp.expander('Drawing rate settings'):
    FPS = st.slider(label='FPS', value=FPS, min_value=0, max_value=30)
    SPF = st.slider(label='SPF', value=SPF, min_value=1, max_value=1000)
    ADAPTIVE_RATE = st.checkbox(label='Use adaptive drawing rate?', value=ADAPTIVE_RATE)
    if ADAPTIVE_RATE:
        draw_rate = st.slider(label='drawing rate coefficient', value=draw_rate, min_value=1, max_value=20000)

with st.sidebar.expander('Base curve settings') as exp1:
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
    tag = '_base'
    for param in base_curve_coeffs:
        if param in 'bd':
            base_curve_coeffs[param] = pi * st.slider(param + tag + ' (pi)', min_value=slider_min[param],
                                                      max_value=2.0, value=round(base_curve_coeffs[param] / pi, 2),
                                                      step=slider_step[param])
        else:
            base_curve_coeffs[param] = st.slider(param + (tag if param in 'ABac' else ''),
                                                 min_value=slider_min[param], value=base_curve_coeffs[param],
                                                 max_value=slider_max[param], step=slider_step[param])
    DISP_BASE_CURVE = st.checkbox('Display base curve', value=False)
    base_curve_image_holder = st.empty()
    if DISP_BASE_CURVE:
        base_curve_image_holder.image(get_base_image())
    else:
        base_curve_image_holder.empty()

with st.sidebar.expander('Curls curve settings'):
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

    curls_x = st.selectbox('curls_x', func_names, index=curls_x_ind)
    curls_y = st.selectbox('curls_y', func_names, index=curls_y_ind)
    rad_ratio = st.slider('Radius ratio (R : r)', value=rad_ratio, min_value=slider_min['R div r'],
                          max_value=slider_max['R div r'], step=slider_step['R div r'])
    speed = st.slider('Speed floor', value=round(speed - speed % 1), min_value=round(slider_min['speed']),
                      max_value=round(slider_max['speed']), step=1) + \
            st.slider('Speed fractional part', value=round(speed % 1, 2), min_value=0.0, max_value=0.99, step=0.01)
    speed = round(speed, 2)
    # speed = speed_int + speed_frac
    # speed = st.slider('Speed', value=speed, min_value=slider_min['speed'], max_value=slider_max['speed'], step=slider_step['speed'])
    outer_params = {'R div r': rad_ratio, 'speed': speed}
    tag = '_curls'
    for param in curls_curve_coeffs:
        if param in 'bd':
            curls_curve_coeffs[param] = pi * st.slider(param + tag + ' (pi)', min_value=slider_min[param],
                                                       max_value=2.0, value=round(curls_curve_coeffs[param] / pi, 2),
                                                       step=slider_step[param])
        else:
            curls_curve_coeffs[param] = st.slider(param + (tag if param in 'ABac' else ''),
                                                  min_value=slider_min[param], value=curls_curve_coeffs[param],
                                                  max_value=slider_max[param], step=slider_step[param])
    DISP_CURLS_CURVE = st.checkbox('Display curls curve pattern', value=False)
    curls_curve_image_holder = st.empty()
    if DISP_CURLS_CURVE:
        curls_curve_image_holder.image(get_curls_image_closeup())
    else:
        curls_curve_image_holder.empty()

with st.sidebar.expander('Radius curve settings'):
    rad_f = st.selectbox('radius function', func_names, index=func_names.index(rad_f))
    radius_curve_coeffs['q'] = q = st.slider('q floor', value=round(q - q % 1), min_value=round(slider_min['q']),
                                             max_value=round(slider_max['q'])) \
                                   + st.slider('fractional part of q', value=round(q % 1, 2), min_value=0.0,
                                               max_value=0.99, step=0.01)
    radius_curve_coeffs['q'] = q
    param = 'C'
    c = radius_curve_coeffs[param] = st.slider(param, min_value=slider_min[param], value=radius_curve_coeffs[param],
                                               max_value=slider_max[param], step=slider_step[param])
    param = 'b'
    radius_curve_coeffs[param] = pi * st.slider(param + '_rad' + ' (pi)', min_value=slider_min[param],
                                                max_value=2.0, value=round(radius_curve_coeffs[param] / pi, 2),
                                                step=slider_step[param])
    ORTHOGONAL_WAVES = st.checkbox(label='Use orthogonal waves effect?', value=ORTHOGONAL_WAVES)
    if ORTHOGONAL_WAVES:
        NORMALISE_WAVES = st.checkbox(label='Use constant amplitude?', value=NORMALISE_WAVES)
    a, c = base_curve_coeffs['a'], base_curve_coeffs['c']

# for i in range(len(curves)):
#     curve = curves[i]
# #     if curve_codes[i] in 'bc':
# #         continue
#     for param in curve:
#         curve[param] = st.sidebar.slider(param + (('_' + curve_codes[i]) if param in 'ABabcd' else ''),
#                                          value=curve[param], min_value=slider_min[param], max_value=slider_max[param],
#                                          step=slider_step[param])

spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
                   base_curve=base_curve_coeffs, curls=curls_curve_coeffs, rad_curve=radius_curve_coeffs,
                   rad_f=rad_f, base_f=(base_x, base_y), curls_f=(curls_x, curls_y),
                   ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES)
name = get_name(spiro.R0, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x,
                curls_y=curls_y, curls_curve_coeffs=curls_curve_coeffs, radius_curve_coeffs=radius_curve_coeffs,
                speed=speed, q=q, rad_f=rad_f)
draw = MyImage(width=WIDTH, height=HEIGHT, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH, name=name, st_res=1000)
# DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
x, y = spiro.get_point()
run = True
image_holder = st.empty()
image_holder.image(draw.st_im)
st.button('Save now!', 'save', on_click=lambda: draw.save(final_save=False))
STOP = False


def flip():
    global STOP
    STOP = not STOP


stop_start = st.button('Pause!', 'ss', on_click=lambda: flip())
i = 0
pause = st.checkbox(label='Pause!!!', key='ppp', value=False)
while spiro.t < 2 * spiro.per * pi + 0.1:
    if not pause:
        x0, y0 = x, y
        x, y = spiro.update(draw_rate=draw_rate)
        colour = get_colour(spiro, colour_scheme_type=COLOURING_SCHEME_BASE, my_colour_scheme=MY_COLOUR_SCHEME,
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
