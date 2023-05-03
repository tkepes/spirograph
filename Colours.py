import numpy as np
from utils import normalise
from Spirograph import Spirograph


def get_colour(spirog: Spirograph, colour=np.array([255, 127, 0]), colouring_scheme_type='', my_colour_scheme=True,
               bipolar_colour_scheme=False, dynamic_shading=True, col2=None):
    cx, cy = colouring_scheme_type + 'x', colouring_scheme_type + 'y'
    if my_colour_scheme:
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
    elif bipolar_colour_scheme:
        if col2 is None:
            col2 = np.array([0, 0, 255])
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
    if dynamic_shading:
        dx, dy = spirog.get_derivatives(x=cx, y=cy)
        d = (dx ** 2 + dy ** 2) ** 0.5
        d = (d / max([d, spirog.get_max_diff(x=cx, y=cy) * 0.9])) ** 1
        # print(d)
        strength = 0.6
        colour = np.round(strength * (1 / strength - (1 - d)) * colour).astype(int)
    if np.any(colour < 0) or np.any(colour > 255):
        colour = (255, 255, 255)
    return tuple(colour)
