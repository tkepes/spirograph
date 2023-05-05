# import numpy as np
# from  numpy import pi as pi
import numpy as np

from utils import get_period
from MyFunctions import *


def get_max(f, g, a, b):
    b = int(round(b + 0.5))
    if b - a > 10 ** 3:
        T = np.linspace(a, a + 10 ** 3, 10 ** 4 + 1)
    else:
        T = np.linspace(a, b, 10 * (b - a) + 1)
    D = [np.sqrt(f(t) ** 2 + g(t) ** 2) for t in T]
    return np.max(D), np.average(D), T


class Spirograph:
    def __init__(self, width=2000, height=2000, ADAPTIVE_RATE=True, outer_params=None, base_curve=None, curls=None,
                 rad_curve=None, ORTHOGONAL_WAVES=False, NORMALISE_WAVES=False, base_f=('cos', 'sin'),
                 curls_f=('cos', 'sin'), rad_f='sin', **kwargs):
        self.f = f
        self.df = df
        self.d2f = d2f
        self.width = width
        self.height = height
        self.ADAPTIVE_RATE = ADAPTIVE_RATE

        r_scale = outer_params['R div r']
        speed = outer_params['speed']
        self.R0 = min(self.width, self.height) // 2 / (1 + 1 / r_scale)
        self.r0 = self.R0 / r_scale
        self.base_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * f[base_f[0]](t, a=a, b=b)
        self.base_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: B * f[base_f[1]](t, a=c, b=d)
        self.dbase_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * df[base_f[0]](t, a=a, b=b)
        self.dbase_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: B * df[base_f[1]](t, a=c, b=d)
        self.f['base_x'] = self.base_x
        self.f['base_y'] = self.base_y
        self.df['base_x'] = self.dbase_x
        self.df['base_y'] = self.dbase_y
        # self.base_y = lambda t: base_curve_coeffs['B'] * sin(t, a=base_curve_coeffs['c'], b=base_curve_coeffs['d'])
        # self.curls_x = lambda t: ribbon_curve['A'] * cos(t, a=ribbon_curve['a'], b=ribbon_curve['b'])
        # self.curls_y = lambda t: ribbon_curve['B'] * sin(t, a=ribbon_curve['c'], b=ribbon_curve['d'])
        self.curls_x = lambda t, A=curls['A'], a=curls['a'], b=curls['b']: A * f[curls_f[0]](t, a=a * speed, b=b)
        self.curls_y = lambda t, B=curls['B'], c=curls['c'], d=curls['d']: B * f[curls_f[1]](-t, a=c * speed, b=d)
        self.dcurls_x = lambda t, A=curls['A'], a=curls['a'], b=curls['b']: A * df[curls_f[0]](t, a=a * speed, b=b)
        self.dcurls_y = lambda t, B=curls['B'], c=curls['c'], d=curls['d']: B * df[curls_f[1]](-t, a=c * speed, b=d)
        self.f['curls_x'] = self.curls_x
        self.f['curls_y'] = self.curls_y
        self.df['curls_x'] = self.dcurls_x
        self.df['curls_y'] = self.dcurls_y
        # self.R = lambda t: radius_curve_coeffs['R'] * ((1 - radius_curve_coeffs['C']) *
        # sin(t, a=radius_curve_coeffs['q'], b=radius_curve_coeffs['b']) + radius_curve_coeffs['C'])
        if ORTHOGONAL_WAVES:
            self.d2base_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * self.d2f[base_f[0]](
                t, a=a, b=b)
            self.d2base_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: -B * self.d2f[base_f[1]](
                t, a=c, b=d)
            my_norm = lambda t: 1
            if NORMALISE_WAVES:
                my_norm = lambda t: norm(t, self.dbase_x, self.dbase_y)
            kk = np.sqrt(self.r0) / 2
            self.rad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0 / kk * (
                    1 - C) * self.dbase_y(t) * f[rad_f](t, a=q, b=b) / my_norm(t)
            self.rad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: -self.R0 / kk * (
                    1 - C) * self.dbase_x(t) * f[rad_f](t, a=q, b=b) / my_norm(t)
            self.drad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0 / kk * (1 - C) * (
                    self.d2base_y(t) * f[rad_f](t, a=q, b=b) + self.dbase_y(t) * df[rad_f](t, a=q, b=b)) / my_norm(t)
            self.drad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: -self.R0 / kk * (1 - C) * (
                    self.d2base_x(t) * f[rad_f](t, a=q, b=b) + self.dbase_x(t) * df[rad_f](t, a=q, b=b)) / my_norm(t)
            self.R = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0
            self.dR = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.d2f['base_x'] = self.d2base_x
            self.d2f['base_y'] = self.d2base_y
        else:
            self.R = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0 * (
                    (1 - C) * f[rad_f](t, a=q, b=b) + C)
            self.dR = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: \
                self.R0 * (1 - C) * df[rad_f](t, a=q, b=b)
            self.rad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.rad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.drad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.drad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
        self.f['rad_x'] = self.rad_x
        self.f['rad_y'] = self.rad_y
        self.df['rad_x'] = self.drad_x
        self.df['rad_y'] = self.drad_y
        self.f['rad'] = self.R
        self.df['rad'] = self.dR
        s = 0
        pow = 2.2
        exp = 2
        self.x = lambda t, scale=r_scale: self.width // 2 + self.R(t) * (
                self.base_x(t) + 1 / scale * self.curls_x(t) + s / scale ** pow * self.curls_x(t, a=speed * (
                speed ** (exp - 1)))) + self.rad_x(t)
        self.y = lambda t, scale=r_scale: self.height // 2 + self.R(t) * (
                self.base_y(t) + 1 / scale * self.curls_y(t) + s / scale ** pow * self.curls_y(t, c=speed * (
                speed ** (exp - 1)))) + self.rad_y(t)
        self.dx = lambda t, scale=r_scale: self.dR(t) * (
                self.base_x(t) + 1 / scale * self.curls_x(t) + s / scale ** pow * self.curls_x(-t, a=speed * (
                speed ** (exp - 1)))) + self.R(t) * (self.dbase_x(t) + 1 / scale * self.dcurls_x(
            t) + s / scale ** pow * self.dcurls_x(-t, a=speed * (speed ** (exp - 1)))) + self.drad_x(t)
        self.dy = lambda t, scale=r_scale: self.dR(t) * (
                self.base_y(t) + 1 / scale * self.curls_y(t) + s / scale ** pow * self.curls_y(-t, c=speed * (
                speed ** (exp - 1)))) + self.R(t) * (self.dbase_y(t) + 1 / scale * self.dcurls_y(
            t) + s / scale ** pow * self.dcurls_y(-t, c=speed * round(speed ** (exp - 1)))) + self.drad_y(t)
        self.f['x'] = self.x
        self.f['y'] = self.y
        self.df['x'] = self.dx
        self.df['y'] = self.dy

        # some other derivatives for colouring
        self.df['(base+curls)_x'] = lambda t: self.dx(t) - self.drad_x(t)
        self.df['(base+curls)_y'] = lambda t: self.dy(t) - self.drad_y(t)
        self.df['(base+rad)_x'] = lambda t: self.dR(t) * self.base_x(t) + self.R(t) * self.dbase_x(t) + \
                                            self.drad_x(t)
        self.df['(base+rad)_y'] = lambda t: self.dR(t) * self.base_y(t) + self.R(t) * self.dbase_y(t) + \
                                            self.drad_y(t)

        self.phi = lambda t, dx=self.dx, dy=self.dy: np.sign(dy(t)) * np.arccos(
            dx(t) / np.sqrt(dx(t) ** 2 + dy(t) ** 2))

        # self.curls_x = lambda t: self.x(t) +
        self.t = 0.0
        # self.rate = 0.03  # 31 * pi / 41  # 6 * 1e-2
        self.rate = 3 * min(0.08 / speed, 0.06)
        nums = (2, max(rad_curve['q'], max(1, s * speed ** exp)), base_curve['a'], base_curve['c'], curls['a'] * speed,
                curls['c'] * speed)
        self.per = np.abs(get_period(2, max(rad_curve['q'], max(1, s * speed ** exp)), base_curve['a'], base_curve['c'],
                                     curls['a'] * speed, curls['c'] * speed))
        if self.per % 1 == 0:
            self.per = round(self.per)
        print(f'A periódus: {self.per}pi')
        print(nums)

        self.max_diff = {}
        self.max_slope, self.av_slope, T = get_max(self.dx, self.dy, 0, self.per * pi)
        print(round(self.max_slope, 2), round(self.av_slope, 2))
        xmax = max([self.x(t) for t in T])
        xmin = min([self.x(t) for t in T])
        ymax = max([self.y(t) for t in T])
        ymin = max([self.y(t) for t in T])
        M = max(xmax - self.width // 2, ymax - self.height // 2, self.width // 2 - xmin, self.height // 2 - ymin)
        rescale_factor = (min(self.width, self.height) // 2 - 50) / M
        self.R0 *= rescale_factor
        self.r0 *= rescale_factor
        self.max_base_slope, self.av_base_slope, _ = get_max(self.dbase_x, self.dbase_y, 0,
                                                             get_period(base_curve['a'], base_curve['c']))
        self.max_curls_slope, self.av_curls_slope, _ = get_max(self.dcurls_x, self.dcurls_y, 0, round(
            get_period(curls['a'], curls['c']) * speed) * pi)
        self.max_diff['x', 'y'] = self.max_slope
        self.max_diff['base_x', 'base_y'] = self.max_base_slope
        self.max_diff['curls_x', 'curls_y'] = self.max_curls_slope
        self.max_diff['curls_x', 'curls_y'] = self.max_curls_slope
        self.max_diff['(base+curls)_x', '(base+curls)_y'] = max(self.max_base_slope, self.max_curls_slope,
                                                                self.max_slope)
        if ORTHOGONAL_WAVES:
            self.max_rad_slope, self.av_rad_slope, _ = get_max(self.drad_x, self.drad_y, 0, rad_curve['q'] * pi)
            self.max_diff['rad_x', 'rad_y'] = self.max_rad_slope
            self.max_diff['(base+rad)_x', '(base+rad)_y'] = max(self.max_base_slope, self.max_rad_slope)

    def update(self, x='x', y='y'):
        if self.ADAPTIVE_RATE:
            delta = (np.sqrt(self.df[x](self.t) ** 2 + self.df[y](self.t) ** 2) / self.max_diff[x, y])
            delta = (delta ** 0.04) / max(np.power(self.per, 0.8), 100)  # 100
            # print(round(delta, 3))
            self.t += delta
        else:
            self.t += self.rate
        return self.f[x](self.t), self.f[y](self.t)

    def get_derivatives(self, t=None, x='x', y='y'):
        if t is None:
            t = self.t
        return self.df[x](t), self.df[y](t)

    def get_base_derivatives(self, t=None):
        if t is None:
            t = self.t
        return self.dbase_x(t), self.dbase_y(t)

    def get_curls_derivatives(self, t):
        if t is None:
            t = self.t
        return self.dcurls_x(t), self.dcurls_y(t)

    def get_max_diff(self, x='x', y='y'):
        return self.max_diff[x, y]

    def generate_curve(self, limit=0, x='x', y='y'):
        t = 0
        points = []
        if self.ADAPTIVE_RATE:
            while t < limit:
                points.append((self.f[x](t), self.f[y](t)))
                t += self.rate
                delta = (np.sqrt(self.df[x](t) ** 2 + self.df[y](t) ** 2) / self.max_diff[x, y])
                delta = (delta ** 0.04) / max(np.power(self.per, 0.7), 100)
                t += delta
        else:
            while t < limit:
                points.append((self.f[x](t), self.f[y](t)))
                t += self.rate
        return points
