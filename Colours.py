import numpy as np
from numpy import pi as pi
from numpy.linalg import norm
from utils import normalise
from Spirograph import Spirograph
from MyFunctions import sin, cos, zin, coz

"""
Each scheme function returns a numpy array of three elements in [-1,1]
And in the get_colour() method this array is transformed into [0,255]**3
"""


def equid_sin_scheme(t, f=sin, a=1, c=1, b=0, s1=0, s2=2 / 3, s3=4 / 3, NORM=False):
    # col_scheme = lambda t, a=1, f=8 / 3, s1=0, s2=1 / 4, s3=1 / 2: \
    #     np.round(255 * (sin(t, a=a, b=f * pi * np.array([s1, s2, s3])) + 1) / 2).astype(int)
    # colour = col_scheme(0.5 * spiro.t)  # spiro.per * spiro.t)
    # # col_scheme1 = lambda t, a=1, f=8 / 3, s1=0, s2=1 / 4, s3=1 / 2: col_scheme0(t, a, f, s1, s2, s3) # - np.min(col_scheme0(t, a, f, s1, s2, s3))
    # # col_scheme = lambda t, a=1, f=8 / 3, s1=0, s2=1 / 4, s3=1 / 2: np.round(255 * col_scheme0(t, a, f, s1, s2, s3))
    return (f(t, a=a, b=b + c * pi * np.array([s1, s2, s3])) + 1) / 2


def diff_scheme(spiro: Spirograph, cx='x', cy='y', f=sin, A=1, a=1, b=0):
    dx, dy = spiro.get_derivatives(x=cx, y=cy)
    dx, dy = normalise(dx, dy)
    z = A * f(a * spiro.t + b)
    if A == 0:
        A = 1
    colour = np.array([dx, dy, z]) / abs(A)
    return colour

def dynamic_shading_factor(spiro: Spirograph, cx='x', cy='y', strength=.3):
    dx, dy = spiro.get_derivatives(x=cx, y=cy)
    d = (dx ** 2 + dy ** 2) ** 0.5
    d = (d / max([d, spiro.get_max_diff(x='d' + cx, y='d' + cy) * 0.9])) ** 1
    return strength * (1 / strength - (1 - d))

def bipolar_scheme0(spiro: Spirograph, col1: np.ndarray, col2: np.ndarray):
    w = abs(spiro.angle()) / pi
    return w * col1 + (1 - w) * col2


def get_colour(spiro: Spirograph, colour=np.array([255, 127, 0]), colour_scheme_type='', my_colour_scheme=True,
               bipolar_colour_scheme=False, dynamic_shading=True, col2=None, NORM=False, FROM_ZERO=False, perm=None):
    cx, cy = colour_scheme_type + 'x', colour_scheme_type + 'y'

    if my_colour_scheme:
        colour = diff_scheme(spiro, cx, cy, sin)
        colour -= np.min(colour)
        colour /= np.linalg.norm(colour)
    elif bipolar_colour_scheme:
        if col2 is None:
            col2 = np.array([0, 0, 255])
        v = (1, 0)
        u = (-v[1], v[0])
        col1 = np.array([0, 0, 255])
        col2 = 255 - col1
        dx, dy = spiro.get_derivatives()
        dx, dy = normalise(dx, dy)
        n1 = v[0] * dx + v[1] * dy
        n2 = u[0] * dx + u[1] * dy
        # phi = np.arccos(u[0] * dx + u[1] * dy) / (np.pi)
        # colour = np.round((max(0, phi - 0.5) * col1 + max(0, 0.5 - phi) * col2)).astype(int)
        # colour = np.round((n1 * col1 + n2 * col2) / (max(n1 + n2, 1))).astype(int)
        colour = (n1 * col1 + n2 * col2) / (max(n1 + n2, 1))
        # colour -= np.min(colour)
        colour = np.round(np.maximum(np.minimum(colour, 255), 0)).astype(int)
    if NORM:
        if FROM_ZERO:
            colour -= np.min(colour)
        colour /= np.linalg.norm(colour)
    if perm is None:
        perm = np.array([0, 1, 2])
    assert len(perm) == 3 and perm[0] in [0, 1, 2] and perm[1] in [0, 1, 2] and perm[2] in [0, 1, 2]
    # 0 in perm and 1 in perm and 2 in perm
    colour = colour[perm]
    if dynamic_shading:
        strength = 0.3
        colour *= dynamic_shading_factor(spiro, cx, cy, strength)
    colour = np.round(255 * colour).astype(int)
    if np.any(colour < 0) or np.any(colour > 255):
        colour = (255, 255, 255)
    return tuple(colour)
