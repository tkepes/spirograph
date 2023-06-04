import os
from datetime import datetime as dt
import numpy as np
import pandas as pd
# import sys
# sys.path.insert(0, '.')
import streamlit as st
from Image import MyImage
from PIL import Image
from Spirograph import Spirograph, pi
from Parameters import *
from Colours import *
from utils import least_multiple, hex_to_rgb, rgb_to_hex

curve_codes = ['outer', 'b', 'c', 'r']
curves = [outer_params, base_curve_coeffs, curls_curve_coeffs, radius_curve_coeffs]
base_choices = ['', 'circle', 'lissajous(1, 2)', 'lissajous(3, 2)', 'lissajous(4, 3)', 'lissajous(5, 4)',
                'lissajous(6, 5)']
st.markdown(
    """
   <style>
   [data-testid="stSidebar"][aria-expanded="true"]{
       min-width: 350px;
       max-width: 50%;
   }
   """,
    unsafe_allow_html=True,
)
st.markdown(
    """
   <style>
   [data-testid=stImage]{
        text-align: center;
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
   }
   """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_base_image(show_sects, base_sect_fact, *args):
    w, h = 300, 300
    base_spiro = Spirograph(width=w, height=h, ADAPTIVE_RATE=ADAPTIVE_RATE, base_curve=base_curve_coeffs,
                            base_f=(base_x, base_y), section_fact=base_sect_fact, draw_rate=draw_rate / 2)
    base_draw = MyImage(width=w, height=h, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH)
    x, y = base_spiro.get_point()
    base_line_width = 3
    while base_spiro.t < 2 * base_spiro.per * pi:
        x0, y0 = x, y
        x, y = base_spiro.update()
        colour = get_colour(base_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, dynamic_shading=DYNAMIC_SHADING,
                            my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME,
                            flip_dsh=FLIP_DYNAMIC_SHADING, strength=strength)
        base_draw.line(x0, y0, x, y, colour=colour, width=base_line_width)
    if show_sects:
        r = round(base_line_width * 0.6)
        for n in range(base_sect_fact * base_spiro.per):
            x, y = base_spiro.get_point(t=n * 2 * pi / base_spiro.per / base_sect_fact)
            base_draw.draw.ellipse([(x - r, y - r), (x + r, y + r)],
                                   fill=(255 - BACKGROUND[0], 255 - BACKGROUND[1], 255 - BACKGROUND[2]))
    return base_draw.im


@st.cache_data
def get_curls_image():
    base_per = least_multiple(least_multiple(base_curve_coeffs['a'], base_curve_coeffs['c']), 2)
    w, h = 1000, 1000
    # print(f'base period: {base_per}, old speed {speed}, new speed: {(speed // 1) // base_per + speed % 1}')
    # , {round((speed // 1) // base_per + speed % 1, 2)}')
    curls_outer_params = {'R div r': outer_params['R div r'], 'speed': round((speed // 1) // base_per + speed % 1, 2)}
    curls_spiro = Spirograph(width=w, height=h, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=curls_outer_params,
                             curls=curls_curve_coeffs, curls_f=(curls_x, curls_y), section_fact=sect_fact,
                             draw_rate=draw_rate / 2)
    curls_draw = MyImage(width=w, height=h, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH)
    x, y = curls_spiro.get_point()
    while curls_spiro.t < curls_spiro.per * pi + 0.1:
        x0, y0 = x, y
        x, y = curls_spiro.update()
        colour = get_colour(curls_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, dynamic_shading=DYNAMIC_SHADING,
                            my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME,
                            flip_dsh=FLIP_DYNAMIC_SHADING, strength=strength)
        curls_draw.line(x0, y0, x, y, colour=colour, width=1)
    print(f'curls_spiro.t = {curls_spiro.t}')
    return curls_draw.im


@st.cache_data
def get_curls_image_closeup(coeffs, *args):
    base_per = get_period(base_curve_coeffs['a'], base_curve_coeffs['c'])
    base_per *= least_multiple(base_curve_coeffs['a'], base_curve_coeffs['c'])
    w_s, h_s = WIDTH, HEIGHT
    curls_speed = round((2 * speed // 1) // base_per + speed % 1, 2)
    curls_outer_params = {'R div r': rad_ratio, 'speed': curls_speed}
    print(f'curls pattern outer params: {curls_outer_params}, base period {base_per}')
    margin = 50
    curls_spiro = Spirograph(width=w_s, height=h_s, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=curls_outer_params,
                             curls=coeffs, curls_f=(curls_x, curls_y), section_fact=sect_fact,
                             margin=margin, draw_rate=draw_rate / 2)
    w = h = 2 * margin + round(2 * curls_spiro.r0)
    line_width = max(round(w_s // w * LINE_WIDTH), 1)
    print(f'width = {w}, width ratio = {w_s / w:.2f}, line width = {line_width}')
    curls_draw = MyImage(width=w, height=h, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH)  # line_width)

    def shift(x, y):
        return x, y - (h_s - h) // 2

    def IsOnImage(t=0):
        x, y = curls_spiro.get_point(t=t)
        x, y = shift(x, y)
        return 0 <= x < w and 0 <= y < h

    t = t_0 = pi
    while curls_spiro.t < curls_spiro.per * pi:
        while IsOnImage(t):
            t -= 0.01
        curls_spiro.t = t
        x, y = curls_spiro.get_point()
        while not IsOnImage(curls_spiro.t):
            # # x0, y0 = x, y # x, y =
            # curls_spiro.update(draw_rate=draw_rate / 2)
            x0, y0 = x, y
            x, y = curls_spiro.update()
            if IsOnImage(curls_spiro.t):
                colour = get_colour(curls_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, strength=strength,
                                    dynamic_shading=DYNAMIC_SHADING, flip_dsh=FLIP_DYNAMIC_SHADING,
                                    my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME)
                x0_d, y0_d = shift(x0, y0)
                x_d, y_d = shift(x, y)
                curls_draw.line(x0_d, y0_d, x_d, y_d, colour=colour)
        x, y = curls_spiro.get_point()
        while IsOnImage(curls_spiro.t):
            x0, y0 = x, y
            x, y = curls_spiro.update()
            colour = get_colour(curls_spiro, colour_scheme_type=COLOURING_SCHEME_BASE, dynamic_shading=DYNAMIC_SHADING,
                                flip_dsh=FLIP_DYNAMIC_SHADING, strength=strength,
                                my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME)
            x0_d, y0_d = shift(x0, y0)
            x_d, y_d = shift(x, y)
            curls_draw.line(x0_d, y0_d, x_d, y_d, colour=colour)
        t_0 += 2 * pi
        t = t_0
    return curls_draw.im


with st.sidebar.expander('Display settings') as disp:
    st.header('Image settings')  # with st.sidebar.expander("Image settings"):
    WIDTH = st.slider('Image width', value=WIDTH, min_value=0, max_value=10000)
    HEIGHT = st.slider('Image height', value=HEIGHT, min_value=0, max_value=10000)
    st.subheader('Display settings')
    BACKGROUND = hex_to_rgb(st.color_picker('Choose a colour for the background!', value=rgb_to_hex(BACKGROUND)))
    LINE_WIDTH = st.slider('Curve width', value=LINE_WIDTH, min_value=1, max_value=20)
    DYNAMIC_SHADING = st.checkbox(label='Dynamic shading', value=DYNAMIC_SHADING)
    dsh_container = st.empty()
    if DYNAMIC_SHADING:
        strength = st.slider('Shading strength', value=strength, min_value=.1, max_value=1., step=.1)
        FLIP_DYNAMIC_SHADING = st.checkbox(label='Flip lighter and darker regions?', value=FLIP_DYNAMIC_SHADING)
    else:
        dsh_container.empty()
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

    st.subheader('Drawing rate settings')  # with disp.expander('Drawing rate settings'):
    FPS = st.slider(label='FPS', value=FPS, min_value=0, max_value=30)
    SPF = st.slider(label='SPF', value=SPF, min_value=1, max_value=1000)
    ADAPTIVE_RATE = st.checkbox(label='Adaptive drawing rate', value=ADAPTIVE_RATE)
    draw_rate_ = st.empty()

with st.sidebar.expander('Base curve settings') as exp1:
    base_text = 'Base(t) = (A base_x(a t + b), B base_y(c t + d))'
    # st.latex('Base(t) = (A\cdot base_x(a\cdot t + b), B\cdot base_y(c\cdot t + d))')

    st.subheader('Base curve formula:')
    st.markdown('Base$(t) = (A\cdot$base$_x(a\cdot t + b)$; $B\cdot$base$_y(c\cdot t + d))$')
    st.markdown('You can customise the base curve below following this formula!')
    # st.header(f'Base(t) = (A base_x(a t + b), B base_y(c t + d))')
    base_choice = st.selectbox('some popular choices', base_choices, index=0)
    if 'lissajous' in base_choice:
        base_x_ind, base_y_ind = 1, 0
        base_a, base_c = int(base_choice[-5]), int(base_choice[-2])
        base_A, base_b, base_d = 1, .0, .0
        if (base_a, base_c) == (1, 2):
            base_A = 2
        else:
            base_b = np.pi / 2
    elif 'circle' in base_choice:
        base_x_ind, base_y_ind = 1, 0
        base_A, base_a, base_b, base_B, base_c, base_d = 1, 1, .0, 1, 1, .0
    else:
        base_x_ind, base_y_ind = 1, 0
        base_A, base_a, base_b, base_B, base_c, base_d = 1, 1, .0, 1, 1, .0
    base_curve_coeffs = {'A': base_A, 'a': base_a, 'b': base_b, 'B': base_B, 'c': base_c, 'd': base_d}
    st.markdown('You can set the value of each coloured parameter below!')
    st.divider()
    col_x, col_y = st.columns([1, 1])


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


    def col_pars_text(x='x', A='A', a='a', b='b'):
        return f'Base$_{x}(t) = $:blue[${coeff_labels[A]}$]$\cdot$:orange[base$_{x}$]$($:red[${coeff_labels[a]}$]$\cdot t$:green[$ + {coeff_labels[b]}$]$)$'


    def func_val_calc0(A='A', a='a', b='b', ff=base_x):
        t, pi_str = 't', '\pi'
        empty = ''
        return f'{str_mult(base_curve_coeffs[A], f"{ff}({str_add(str_mult(base_curve_coeffs[a], t, prod_char=empty), str_mult(round(base_curve_coeffs[b] / pi, 2), pi_str, prod_char=empty))})", prod_char=empty)}'


    def func_val_calc(x='x', A='A', a='a', b='b', ff=base_x):
        return f'Base$_{x}(t) = {func_val_calc0(A=A, a=a, b=b, ff=ff)}$'


    col_x.subheader('Base$_x$:')
    col_y.subheader('Base$_y$:')
    col_x.markdown(col_pars_text())
    col_y.markdown(col_pars_text('y', 'B', 'c', 'd'))
    base_x = col_x.selectbox(par_cols[base_x]('base$_x$'), func_names, index=base_x_ind)
    base_y = col_y.selectbox(par_cols[base_y]('base$_y$'), func_names, index=base_y_ind)
    tag = ''  # f'_base'
    cont = {'A': col_x, 'a': col_x, 'b': col_x, 'B': col_y, 'c': col_y, 'd': col_y}
    for param in base_curve_coeffs:
        if param in 'bd':
            # cont[param].markdown(col_setter(param + tag + ' (pi)', col=coeff_cols[param]))
            base_curve_coeffs[param] = pi * cont[param].slider(
                par_cols[param](f'${coeff_labels[param]}$') + tag + ' $(\cdot\pi)$',
                min_value=slider_min[param],
                max_value=2.,
                value=round(base_curve_coeffs[param] / pi, 1))
            # , step=round(slider_step[param] / pi, 1))
        else:
            # cont[param].markdown(par_cols[param](param + (tag if param in 'ABac' else '')))
            base_curve_coeffs[param] = cont[param].slider(
                label=par_cols[param](f'${coeff_labels[param]}$') + (tag if param in 'ABac' else ''),
                min_value=slider_min[param], value=base_curve_coeffs[param],
                max_value=slider_max[param], step=slider_step[param])

    col_x.markdown(func_val_calc())
    col_y.markdown(func_val_calc('y', 'B', 'c', 'd', ff=base_y))
    st.divider()
    st.markdown(
        f'Choosen curve:\n :black[Base$(t) = ({func_val_calc0()};$ ${func_val_calc0("B", "c", "d", ff=base_y)})$]')
    DISP_BASE_CURVE = st.checkbox('Display base curve', value=False)
    show_sects = st.empty()
    sect_slid = st.empty()
    base_curve_image_holder = st.empty()
    if DISP_BASE_CURVE:
        show_sects = st.checkbox('Show sections?', value=False)
        if show_sects:
            base_sect_fact_max = 10 * (
                    least_multiple(base_curve_coeffs['a'], base_curve_coeffs['c']) + max(base_curve_coeffs['a'],
                                                                                         base_curve_coeffs['c']))
            # ** 2 // max(base_curve_coeffs['a'], base_curve_coeffs['c']))
            base_sect_fact = sect_slid.slider('Section factor', value=base_sect_fact, min_value=1,
                                              max_value=base_sect_fact_max)
        else:
            sect_slid.empty()
        base_curve_image_holder.image(
            get_base_image(show_sects, base_sect_fact, base_x, base_y, base_curve_coeffs, COLOURING_SCHEME_BASE,
                           LINE_WIDTH,
                           DYNAMIC_SHADING, FLIP_DYNAMIC_SHADING, BACKGROUND, strength, MY_COLOUR_SCHEME))
    else:
        show_sects.empty()
        sect_slid = st.empty()
        base_curve_image_holder.empty()

with st.sidebar.expander('Curls curve settings'):
    my_curls = None
    if st.checkbox('Show curls curve?', value=True):
        # curls_choices = base_choices
        # curls_choice = st.selectbox('curls choices', curls_choices, index=0)
        # if 'lissajous' in curls_choice:
        #     curls_x_ind, curls_y_ind = 1, 0
        #     a, c = int(curls_choice[-5]), int(curls_choice[-2])
        #     lm = least_multiple(a, c)
        #     rad_ratio, speed = 2 * lm, 3 * lm + 0.12
        #     # if (a, c) == (1, 2):
        #     #     rad_ratio, speed = 4, 7.12
        #     #     # rad_ratio, speed = 4, 1.04
        #     # elif (a, c) == (3, 2):
        #     #     rad_ratio, speed = 12, 12.05
        #     # elif (a, c) == (4, 3):
        #     #     rad_ratio, speed = 12, 12.05
        #     # else:
        #     #     rad_ratio, speed = 8, 20.24
        # elif 'circle' in curls_choice:
        #     rad_ratio, speed = 2, 1.04
        #     curls_x_ind, curls_y_ind = 1, 0
        # else:
        #     curls_x_ind, curls_y_ind = 1, 0
        adj_r_and_s = st.checkbox('Adjust speed and curls radius to base curve settings?', value=False)
        if adj_r_and_s:
            base_per = get_period(base_curve_coeffs['a'], base_curve_coeffs['c'])
            base_per *= least_multiple(base_curve_coeffs['a'], base_curve_coeffs['c'])
            base_per //= 2
            speed = round(speed % 1, 2) + base_per
            rad_ratio = max(4, round(5.5 * np.log(base_per)))
            outer_params = {'R div r': rad_ratio, 'speed': speed}

        curls_x_ind, curls_y_ind = 1, 0
        curls_x = st.selectbox('curls_x', func_names, index=curls_x_ind)
        curls_y = st.selectbox('curls_y', func_names, index=curls_y_ind)
        rad_ratio = st.slider('Radius ratio (R : r)', value=rad_ratio, min_value=slider_min['R div r'],
                              max_value=slider_max['R div r'], step=slider_step['R div r'])
        speed = st.slider('Speed floor', value=round(speed - speed % 1), min_value=round(slider_min['speed']),
                          max_value=round(slider_max['speed']), step=1) + \
                st.slider('Speed fractional part', value=round(speed % 1, 2), min_value=0., max_value=.99, step=.01)
        speed = round(speed, 2)
        # speed = speed_int + speed_frac
        # speed = st.slider('Speed', value=speed, min_value=slider_min['speed'], max_value=slider_max['speed'], step=slider_step['speed'])
        outer_params = {'R div r': rad_ratio, 'speed': speed}
        tag = '_curls'
        for param in curls_curve_coeffs:
            if param in 'bd':
                curls_curve_coeffs[param] = pi * st.slider(param + tag + ' (pi)', min_value=slider_min[param],
                                                           max_value=2., value=round(curls_curve_coeffs[param] / pi, 1))
                # step=round(slider_step[param] / pi, 1))
            else:
                curls_curve_coeffs[param] = st.slider(param + (tag if param in 'ABac' else ''),
                                                      min_value=slider_min[param], value=curls_curve_coeffs[param],
                                                      max_value=slider_max[param], step=slider_step[param])
        DISP_CURLS_CURVE = st.checkbox('Show curls curve pattern', value=False)
        my_curls = curls_curve_coeffs
        curls_curve_image_holder = st.empty()
        if DISP_CURLS_CURVE:
            curls_curve_image_holder.image(
                get_curls_image_closeup(my_curls, adj_r_and_s, outer_params, curls_x, curls_y,
                                        COLOURING_SCHEME_BASE, LINE_WIDTH, DYNAMIC_SHADING, FLIP_DYNAMIC_SHADING,
                                        BACKGROUND, strength, MY_COLOUR_SCHEME))
        else:
            curls_curve_image_holder.empty()

with st.sidebar.expander('Radius curve settings'):
    if st.checkbox('Show radius curve?', value=True):
        rad_f = st.selectbox('radius function', func_names, index=func_names.index(rad_f))
        radius_curve_coeffs['q'] = q = st.slider('q floor', value=round(q - q % 1), min_value=round(slider_min['q']),
                                                 max_value=round(slider_max['q']))  # \
        # + st.slider('fractional part of q', value=round(q % 1, 2), min_value=0.0,
        #             max_value=0.99, step=0.01)
        radius_curve_coeffs['q'] = q
        param = 'C'
        c = radius_curve_coeffs[param] = st.slider(param, min_value=slider_min[param], value=radius_curve_coeffs[param],
                                                   max_value=slider_max[param], step=slider_step[param])
        param = 'b'
        radius_curve_coeffs[param] = pi * st.slider(param + '_rad' + ' (pi)', min_value=slider_min[param],
                                                    max_value=2., value=round(radius_curve_coeffs[param] / pi, 1),
                                                    step=.1)
        rad_choices = ['center', 'orthogonal']
        ORTHOGONAL_WAVES = st.checkbox(label='Orthogonal waves', value=ORTHOGONAL_WAVES)
        nw = st.empty()
        if ORTHOGONAL_WAVES:
            NORMALISE_WAVES = nw.checkbox(label='Constant amplitude', value=NORMALISE_WAVES)
            rad_funcs = ['sin', 'cos', 'zin', 'coz', 'dsin', 'dcos', 'dzin', 'dcoz', 'd2sin', 'd2cos', 'd2zin', 'd2coz',
                         'base_x', 'base_y', 'curls_x', 'curls_y', 'rad', 'x', 'y', 'dbase_x', 'dbase_y', 'dcurls_x',
                         'dcurls_y', 'drad', 'dx', 'dy', 'd(base+curls)_x', 'd(base+curls)_y', 'd(base+rad)_x',
                         'd(base+rad)_y', 'd2base_x', 'd2base_y', 'd2curls_x', 'd2curls_y', 'd2rad', 'd2x', 'd2y']
            rad_x = st.selectbox('rad_x', rad_funcs, index=rad_funcs.index(rad_x))
            rad_y = st.selectbox('rad_y', rad_funcs, index=rad_funcs.index(rad_y))
        else:
            nw.empty()

# for i in range(len(curves)):
#     curve = curves[i]
# #     if curve_codes[i] in 'bc':
# #         continue
#     for param in curve:
#         curve[param] = st.sidebar.slider(param + (('_' + curve_codes[i]) if param in 'ABabcd' else ''),
#                                          value=curve[param], min_value=slider_min[param], max_value=slider_max[param],
#                                          step=slider_step[param])


lim_max = 500
lim1 = st.empty()  # slider('red curvture min', key='rcmn', value=20, max_value=lim_max)
lim2 = st.empty()  # slider('red curvture max', key='rcmx', value=20, min_value=lim1, max_value=lim_max)


# @st.cache_data
def draw_curve(**kwargs):
    spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
                       base_curve=base_curve_coeffs, curls=my_curls, rad_curve=radius_curve_coeffs, draw_rate=None,
                       rad_f=rad_f, base_f=(base_x, base_y), curls_f=(curls_x, curls_y), rad_coeffs=rad_xy_coeffs,
                       ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES, section_fact=sect_fact)
    scale = round(spiro.scale)
    spiro.draw_rate = draw_rate_.slider(label='drawing rate coefficient', value=scale, min_value=1,
           max_value=100 * scale)

    pause = False
    global lim_max
    lim_max = round(spiro.curv_max) + 1
    lim_1 = lim1.slider('red curvture min', value=20, max_value=lim_max)
    lim_2 = lim2.slider('red curvture max', value=lim_1, min_value=lim_1, max_value=lim_max)

    def from_temp():
        if 'temp.png' in os.listdir(os.getcwd() + '/Images/'):
            # print(os.listdir(os.getcwd() + '/Images/'))
            global draw
            draw = MyImage(im=Image.open('Images/temp.png'), st_res=1000,
                           st_im=Image.open('Images/temp_st.png'), BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH,
                           name=name)
            with open('Images/temp.txt', 'r') as file:
                spiro.t = float(file.readline().strip())
            # x, y = spiro.get_point()
            # if not pause:
            #     os.remove(os.getcwd() + '/Images/temp.png')
            #     os.remove(os.getcwd() + '/Images/temp_st.png')
            #     os.remove(os.getcwd() + '/Images/temp.txt')

    if 'temp.png' in os.listdir(os.getcwd() + '/Images/'):
        with open('Images/temp.txt', 'r') as file:
            spiro.t = float(file.readline().strip())
            name = file.readline().strip()
            stage = int(file.readline().strip())
            path = file.readline().strip()
        draw = MyImage(im=Image.open('Images/temp.png'), st_res=1000, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH,
                       st_im=Image.open('Images/temp_st.png'), name=name, path=path)
        draw.stage = stage
        os.remove(os.getcwd() + '/Images/temp.png')
        os.remove(os.getcwd() + '/Images/temp_st.png')
        os.remove(os.getcwd() + '/Images/temp.txt')
    else:
        name = get_name(spiro.R0, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x,
                        curls_y=curls_y, curls_curve_coeffs=curls_curve_coeffs, radius_curve_coeffs=radius_curve_coeffs,
                        speed=speed, q=q, rad_f=rad_f)
        draw = MyImage(width=WIDTH, height=HEIGHT, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH, name=name, st_res=1000)
    # DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
    global x, y
    x, y = spiro.get_point()
    run = True
    image_holder = st.empty()
    image_holder.image(draw.st_im)

    save_but = st.empty()
    stop_start = st.empty()
    STOP = True

    def temp_save(b=pause, write_stage=False):
        if not b:
            print('temp save')
            draw.save(name='temp')
            with open('Images/temp.txt', 'w') as file:
                file.write(str(spiro.t) + '\n')
                file.write(name + '\n')
                file.write(str(draw.stage + write_stage) + '\n')
                file.write(str(draw.PATH) + '\n')
        # else:
        #     from_temp()

    def save_now():
        st.session_state.image_holder = draw.im
        draw.save(final_save=False)
        with open('Images/temp.txt', 'w') as file:
            file.write(str(spiro.t) + '\n')
            file.write(name + '\n')
            file.write(str(draw.stage) + '\n')
            file.write(str(draw.PATH) + '\n')
        print('saving to', str(draw.PATH)[:30] + '...')
        print('stage:', draw.stage)
        draw.save(name='temp')

    # save_but.button('Save now!', 'save', on_click=save_now())

    # with open(str(draw.PATH), "rb") as fp:
    #     btn = st.download_button(
    #         label="Download IMAGE",
    #         data=fp,
    #         file_name=draw.get_save_name(name, final_save=False),
    #         mime="image/ong"
    #     )
    # def flip():
    #     global STOP
    #     STOP = not STOP
    #     if STOP:
    #         stop_start.empty()
    #         stop_start.button('Start!', 'start', on_click=lambda: flip())
    #     else:
    #         stop_start.empty()
    #         stop_start.button('Pause!', 'pause', on_click=lambda: flip())
    #         temp_save(STOP)
    #
    #
    # flip()

    # pause = st.checkbox(label='Pause!!!', key='ppp', value=False, on_change=lambda: temp_save(pause))
    # # if pause:
    # #     temp_save(pause)
    # if not pause and 'temp.png' in os.listdir(os.getcwd() + '/Images/'):
    #     os.remove(os.getcwd() + '/Images/temp.png')
    #     os.remove(os.getcwd() + '/Images/temp_st.png')
    #     os.remove(os.getcwd() + '/Images/temp.txt')

    global i
    i = 0

    def iter():
        global x, y, i
        if not pause:
            x0, y0 = x, y
            curvature = spiro.curvature(spiro.t)
            x, y = spiro.update()
            colour = get_colour(spiro, colour_scheme_type=COLOURING_SCHEME_BASE, my_colour_scheme=MY_COLOUR_SCHEME,
                                bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME, dynamic_shading=DYNAMIC_SHADING,
                                flip_dsh=FLIP_DYNAMIC_SHADING, strength=strength,
                                test_line_lengths=True, ind=i,
                                curvature_test=False, lim1=lim_1, lim2=lim_2, curvature=curvature)
            draw.line(x0, y0, x, y, colour=colour, width=LINE_WIDTH)
            if i % SPF == 0:
                image_holder.image(draw.st_im)
                # temp_im = MyImage(im=draw.im, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH, name=name, st_res=1000,
                #                   st_im=draw.st_im)
            i += 1

    progbar = st.progress(0, text='0%')

    while spiro.t < spiro.per * pi:
        perc = spiro.t / spiro.per / pi
        progbar.progress(perc, f'{100 * perc:.1f}%')
        iter()
        # else:
        #     from_temp()
    # iter()
    progbar.empty()
    image_holder.image(draw.st_im)
    if 'temp.png' in os.listdir(os.getcwd() + '/Images/'):
        os.remove(os.getcwd() + '/Images/temp.png')
        os.remove(os.getcwd() + '/Images/temp_st.png')
        os.remove(os.getcwd() + '/Images/temp.txt')
    name = get_name(spiro.R0, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs, curls_x=curls_x,
                    curls_y=curls_y, curls_curve_coeffs=curls_curve_coeffs, radius_curve_coeffs=radius_curve_coeffs,
                    speed=speed, q=q, rad_f=rad_f)
    draw.save(name=name, final_save=True)


draw_curve(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
           base_curve=base_curve_coeffs,
           curls=my_curls, rad_curve=radius_curve_coeffs, rad_f=rad_f, base_f=(base_x, base_y),
           curls_f=(curls_x, curls_y),
           rad_coeffs=rad_xy_coeffs, ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES,
           section_fact=sect_fact, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH,
           colour_scheme_type=COLOURING_SCHEME_BASE,
           my_colour_scheme=MY_COLOUR_SCHEME, bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME,
           dynamic_shading=DYNAMIC_SHADING, draw_rate=draw_rate_,
           flip_dsh=FLIP_DYNAMIC_SHADING, strength=strength, lim1=lim1, lim2=lim2)
