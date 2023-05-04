import numpy as np
import sys

sys.path.insert(0, '.')
import streamlit as st
from Image import MyImage
from Spirograph import Spirograph
from Parameters import *
from Colours import *

curve_codes = ['outer', 'b', 'c', 'r']
curves = [outer_params, base_curve_coeffs, curls_curve_coeffs, radius_curve_coeffs]

for i in range(len(curves)):
    curve = curves[i]
    for param in curve:
        print(param)
        curve[param] = st.sidebar.slider(param + (('_' + curve_codes[i]) if param in 'ABabcd' else ''),
                                         value=curve[param])

spiro = Spirograph(width=WIDTH, height=HEIGHT, ADAPTIVE_RATE=ADAPTIVE_RATE, outer_params=outer_params,
                   base_curve=base_curve_coeffs, curls=curls_curve_coeffs, rad_curve=radius_curve_coeffs,
                   rad_f=rad_f, base_f=(base_x, base_y), curls_f=(curls_x, curls_y),
                   ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES)
draw = MyImage(width=WIDTH, height=HEIGHT, BACKGROUND=BACKGROUND, LINE_WIDTH=LINE_WIDTH, name=get_name(spiro.R0),
               st_res=1000)
# DYNAMIC_SHADING=True, MY_COLOUR_SCHEME=True, BIPOLAR_COLOUR_SCHEME=False,
x, y = spiro.update()
run = True
image_holder = st.empty()
image_holder.image(draw.st_im)
st.button('Save now!', 'save', on_click=lambda: draw.save(final_save=False))
while spiro.t < 2 * spiro.per:
    x0, y0 = x, y
    x, y = spiro.update()
    colour = get_colour(spiro, colouring_scheme_type=COLOURING_SCHEME_TYPE, my_colour_scheme=MY_COLOUR_SCHEME,
                        bipolar_colour_scheme=BIPOLAR_COLOUR_SCHEME, dynamic_shading=DYNAMIC_SHADING)
    draw.line(x0, y0, x, y, colour=colour, width=LINE_WIDTH)
    image_holder.image(draw.st_im)
draw.save(name=get_name(), final_save=True)
