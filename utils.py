import os
import numpy as np


def rgb_to_hex(rgb):
    HEXCHARS = '0123456789ABCDEF'
    hex = '#'
    for c in tuple(rgb):
        hex += HEXCHARS[round(c // 16)] + HEXCHARS[round(c % 16)]
    # hex = f'#{HEXCHARS[round(r // 16)]}{HEXCHARS[round(r % 16)]}{HEXCHARS[round(g // 16)]}
    #       {HEXCHARS[round(g % 16)]}{HEXCHARS[round(b // 16)]}{HEXCHARS[round(b % 16)]}'
    return hex


def hex_to_rgb(hex):
    hex = hex.upper()
    assert len(hex) == 7
    HEXCHARS = '0123456789ABCDEF'
    rgb = []
    for i in range(1, len(hex), 2):
        rgb += [(HEXCHARS.index(hex[i]) + 1) * (HEXCHARS.index(hex[i + 1]) + 1) - 1]
    return tuple(rgb)


def euclidean(a, b):
    while a % b != 0:
        a, b = b, a % b
    return max(1, b)


def smallest_int_multiplier(a):
    if a % 1 == 0:
        return 1
    decimal_places = len(str(a)) - str(a).index('.') - 1
    b = 10 ** decimal_places
    c = euclidean(round(a * b), b)
    return b // c


def smallest_even_multiplier(a):
    if a % 2 == 0:
        return 1
    elif a % 2 == 1:
        return 2
    b = smallest_int_multiplier(a)
    print(a, b, b / a, end=' ')
    b *= round(a * b) % 2 + 1
    print(b)
    return b


def least_multiple(a, b):
    return a * b // euclidean(a, b)


def get_period(*nums):
    nums = list(nums)
    while 0 in nums:
        nums.remove(0)
    for i in range(len(nums)):
        nums[i] = round(smallest_even_multiplier(nums[i]))
    # print(nums)
    while len(nums) > 1:
        j = len(nums) - 1
        while j > 0:
            nums = nums[:j - 1] + [least_multiple(nums[j], nums[j - 1])] + nums[j + 1:]
            j -= 2
    if len(nums) == 0:
        nums = [1]
    per = abs(nums[0])
    if per % 1 == 0:
       per = round(per)
    return per


def get_name(spirog):
    # x = A * R0 * cos(at) + B * r0 * cos(bwt)
    # y = C * R0 * sin(ct) - D * r0 * sin(dwt)
    # speed = w
    # draw_rate = t_{n+1} - t_n
    st = ('R div r = {' + (':.2f' if '.' in str(spirog.r0 / spirog.r0) else '') +
          '}, q = {}, draw_rate = {:.2f}, speed = {:.2f}').format(spirog.r0 / spirog.r0, spirog.q, spirog.draw_rate,
                                                                  spirog.speed)
    args = spirog.get_params()
    for i in range(8):
        if args[i] != 1:
            st += ', ' + 'ABCDabcd'[i] + (' = {' + (':.2f' if '.00' not in str(args[i]) else '') + '}').format(args[i])
    for i in range(4):
        if args[i + 8] != 0:
            st += ', ' + 'Tt'[i // 2] + 'cs'[i % 2] + ' = {}'.format(args[i + 8])
    return st


def get_name2(curves, codes, defaults, outer_params):
    name = ''
    for key, val in outer_params.items():
        name += f'{key} = {val}, '
    for i in range(len(curves)):
        curve = curves[i]
        for key, val in curve.items():
            key += (('_' + codes[i]) if key in 'ABabcd' else '')
            if val != defaults[key]:
                name += key + (' = {' + (':.2f' if val % 1 > 0.01 else '') + '}').format(val) + ', '
    name = name[:-2]
    return name


def normalise(*nums):
    if len(nums) < 2:
        raise ValueError
    norm = (sum([n ** 2 for n in nums])) ** 0.5
    return [n / norm for n in nums]


def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def get_colour(params, spirog, colour=np.array([255, 127, 0])):
    if params.MY_COLOUR_SCHEME:
        dx, dy = spirog.get_derivatives(params.COLOURING_SCHEME_BASE)
        dx, dy = normalise(dx, dy)
        z = 1 * np.sin(spirog.t)
        # dx, dy, z = normalise(dx, dy, z)
        # d = np.cos(np.pi / 3 * spirog.t)
        # dx, dy, z = dx, dy + d, z + d
        m = min(dx, dy, z)
        dx, dy, z = dx - m, dy - m, z - m
        dx, dy, z = normalise(dx, dy, z)
        colour = np.round(255 * np.array([dx, dy, z])).astype(int)
    elif params.BIPOLAR_COLOUR_SCHEME:
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
    if params.DYNAMIC_SHADING:
        dx, dy = spirog.get_derivatives(type=params.COLOURING_SCHEME_BASE)
        d = (dx ** 2 + dy ** 2) ** 0.5
        d = (d / max([d, spirog.get_max_diff(type=params.COLOURING_SCHEME_BASE) * 0.9])) ** 1
        # print(d)
        strength = 0.6
        colour = np.round(strength * (1 / strength - (1 - d)) * colour).astype(int)
    return tuple(colour)


def generate_curve(spirog, limit=0, x=None, y=None, dx=None, dy=None):
    if x is None:
        x = spirog.x
        dx = spirog.dx
    if y is None:
        y = spirog.x
        dy = spirog.dy
    t = 0
    points = []
    colours = []
    if spirog.ADAPTIVE_RATE:
        while t < limit:
            points.append((x(t), y(t)))
            t += spirog.draw_rate
            delta = (np.sqrt(dx(t) ** 2 + dy(t) ** 2) / spirog.max_slope)
            delta = (delta ** 0.04) / 100
            t += delta
    else:
        while t < limit:
            points.append((x(t), y(t)))
            t += spirog.draw_rate
    return points
