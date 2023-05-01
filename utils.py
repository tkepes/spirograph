import os
import numpy as np


def euclidean(a, b):
    while a % b != 0:
        a, b = b, a % b
    return max(1, b)


def smallest_int_multiple(a):
    if a % 1 == 0:
        return a
    decimal_places = len(str(a)) - str(a).index('.') - 1
    b = 10 ** decimal_places
    c = euclidean(round(a * b), b)
    return b // c


def least_multiple(a, b):
    return a * b // euclidean(a, b)


def least_multiple_of(*nums):
    nums = list(nums)
    for i in range(len(nums)):
        nums[i] = smallest_int_multiple(nums[i])
    while len(nums) > 1:
        j = len(nums) - 1
        while j > 0:
            nums = nums[:j - 1] + [least_multiple(nums[j], nums[j - 1])] + nums[j + 1:]
            j -= 2
    return nums[0]


def get_period(*nums):
    nums = list(nums)
    while len(nums) > 1:
        j = len(nums) - 1
        while j > 0:
            a, b = str(nums[j]), str(nums[j - 1])
            t = 0
            n2 = [a, b]
            for c in n2:
                if '.' in c:
                    t = max(t, len(c[c.index('.') + 1:]))
            if t > 0:
                for i in range(2):
                    if '.' not in n2[i]:
                        n2[i] = n2[i] + '0' * t
                    else:
                        n2[i] = n2[i].replace('.', '') + '0' * (t - len(n2[i][n2[i].index('.') + 1:]))
            a, b = int(n2[0]), int(n2[1])

            c = a * b // euclidean(a, b) // 10 ** t
            nums = nums[:j - 1] + [c] + nums[j + 1:]
            j -= 2
    return nums[0]


def get_name(spirog):
    # x = A * R0 * cos(at) + B * r0 * cos(bwt)
    # y = C * R0 * sin(ct) - D * r0 * sin(dwt)
    # speed = w
    # rate = t_{n+1} - t_n
    name = 'f(t) = '
    if spirog.q != 0:
        name += 'R(t)'
    elif spirog.r0 != 0:
        name += '{:.2f}'.format(spirog.R0 / spirog.r0)
    else:
        name += '{}'.format(spirog.R0)
    name += '(x(t), y(t)), x(t) = ('
    if spirog.A * spirog.R0 != 0:
        name += str(spirog.R0)
        if spirog.A != 1:
            name += '*{}'.format(spirog.A)
        if spirog.a != 0:
            name += 'cos('
            if spirog.a != 1:
                name += '{}'.format(spirog.a)
            name += 't'
            if spirog.Tc != 0:
                name += '{:.2f}'.format(spirog.Tc) if spirog.Tc % 1 != 0 else str(round(spirog.Tc))
            name += ')'
        else:
            name += '{:.2f}'.format(np.cos(spirog.Tc))
        if spirog.r0 * spirog.B != 0:
            name += ' + '
            if spirog.r0 != 1:
                name += str(spirog.r0)
                if spirog.B != 1:
                    name += '*{}'.format(spirog.B)
            elif spirog.B != 1:
                name += '{}'.format(spirog.B)
            if spirog.b != 0:
                name += ''
            name += ''
            name += ''
            name += ''

        name += '), y(t) = ('

    st = ('R div r = {' + (':.2f' if '.' in str(spirog.r0 / spirog.r0) else '') +
          '}, q = {}, rate = {:.2f}, speed = {:.2f}').format(spirog.r0 / spirog.r0, spirog.q, spirog.rate, spirog.speed)
    args = spirog.get_params()
    for i in range(8):
        if args[i] != 1:
            st += ', ' + 'ABCDabcd'[i] + (' = {' + (':.2f' if '.00' not in str(args[i]) else '') + '}').format(args[i])
    for i in range(4):
        if args[i + 8] != 0:
            st += ', ' + 'Tt'[i // 2] + 'cs'[i % 2] + ' = {}'.format(args[i + 8])
    return st


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
        dx, dy = spirog.get_derivatives(params.COLOURING_SCHEME_TYPE)
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
        dx, dy = spirog.get_derivatives(type=params.COLOURING_SCHEME_TYPE)
        d = (dx ** 2 + dy ** 2) ** 0.5
        d = (d / max([d, spirog.get_max_diff(type=params.COLOURING_SCHEME_TYPE) * 0.9])) ** 1
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
            t += spirog.rate
            delta = (np.sqrt(dx(t) ** 2 + dy(t) ** 2) / spirog.max_slope)
            delta = (delta ** 0.04) / 100
            t += delta
    else:
        while t < limit:
            points.append((x(t), y(t)))
            t += spirog.rate
    return points
