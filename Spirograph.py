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
        global f, df, d2f, d3f
        # self.f, self.df, self.d2f = f, df, d2f
        self.width, self.height = width, height
        self.ADAPTIVE_RATE = ADAPTIVE_RATE
        if base_curve is None:
            base_curve = {'A': 1, 'a': 1, 'b': 0, 'B': 1, 'c': 1, 'd': 0}
        # base curve
        base_x, base_y = base_f[0], base_f[1]
        self.base_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * f[base_x](t, a=a, b=b)
        self.base_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: B * f[base_y](t, a=c, b=d)
        # self.base_y = lambda t: base_curve_coeffs['B'] * sin(t, a=base_curve_coeffs['c'], b=base_curve_coeffs['d'])
        self.dbase_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * df[base_x](t, a=a, b=b)
        self.dbase_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: B * df[base_y](t, a=c, b=d)
        self.d2base_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * d2f[base_x](t, a=a, b=b)
        self.d2base_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: -B * d2f[base_y](t, a=c, b=d)
        f['base_x'], f['base_y'] = self.base_x, self.base_y
        df['base_x'], df['base_y'] = self.dbase_x, self.dbase_y
        d2f['base_x'], d2f['base_y'] = self.d2base_x, self.d2base_y
        # curls curve and radius
        if outer_params is None:
            outer_params = {'R div r': 1, 'speed': 1}
        r_scale = outer_params['R div r']
        speed = outer_params['speed']
        self.R0 = min(self.width, self.height) // 2 / (1 + 1 / r_scale)
        self.r0 = self.R0 / r_scale
        if curls is None:
            curls = {'A': 0, 'a': 1, 'b': 0, 'B': 0, 'c': 1, 'd': 0}
        # self.curls_x = lambda t: ribbon_curve['A'] * cos(t, a=ribbon_curve['a'], b=ribbon_curve['b'])
        # self.curls_y = lambda t: ribbon_curve['B'] * sin(t, a=ribbon_curve['c'], b=ribbon_curve['d'])
        curls_x, curls_y = curls_f[0], curls_f[1]
        self.curls_x = lambda t, A=curls['A'], a=curls['a'], b=curls['b']: A * f[curls_x](t, a=a * speed, b=b)
        self.curls_y = lambda t, B=curls['B'], c=curls['c'], d=curls['d']: B * f[curls_y](-t, a=c * speed, b=d)
        self.dcurls_x = lambda t, A=curls['A'], a=curls['a'], b=curls['b']: A * df[curls_x](t, a=a * speed, b=b)
        self.dcurls_y = lambda t, B=curls['B'], c=curls['c'], d=curls['d']: B * df[curls_y](-t, a=c * speed, b=d)
        self.d2curls_x = lambda t, A=curls['A'], a=curls['a'], b=curls['b']: A * d2f[curls_x](t, a=a * speed, b=b)
        self.d2curls_y = lambda t, B=curls['B'], c=curls['c'], d=curls['d']: B * d2f[curls_y](-t, a=c * speed, b=d)
        f['curls_x'], f['curls_y'] = self.curls_x, self.curls_y
        df['curls_x'], df['curls_y'] = self.dcurls_x, self.dcurls_y
        d2f['curls_x'], d2f['curls_y'] = self.d2curls_x, self.d2curls_y
        # self.R = lambda t: radius_curve_coeffs['R'] * ((1 - radius_curve_coeffs['C']) *
        # sin(t, a=radius_curve_coeffs['q'], b=radius_curve_coeffs['b']) + radius_curve_coeffs['C'])
        if rad_curve is None:
            rad_curve = {'C': 1, 'q': 0, 'b': 0}
        if ORTHOGONAL_WAVES:
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
            self.d3base_x = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * d3f[base_x](t, a=a,
                                                                                                               b=b)
            self.d3base_y = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: -B * d3f[base_y](t, a=c,
                                                                                                                b=d)
            self.d2rad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0 / kk * (1 - C) * (
                    self.d3base_y(t) * f[rad_f](t, a=q, b=b) + 2 * self.d2base_y(t) * df[rad_f](t, a=q, b=b) +
                    self.dbase_y(t) * d2f[rad_f](t, a=q, b=b)) / my_norm(t)
            self.d2rad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: -self.R0 / kk * (1 - C) * (
                    self.d3base_x(t) * f[rad_f](t, a=q, b=b) + 2 * self.d2base_x(t) * df[rad_f](t, a=q, b=b) +
                    self.dbase_x(t) * d2f[rad_f](t, a=q, b=b)) / my_norm(t)
            self.R = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0
            self.dR = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.d2R = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
        else:
            self.R = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: self.R0 * (
                    (1 - C) * f[rad_f](t, a=q, b=b) + C)
            self.dR = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: \
                self.R0 * (1 - C) * df[rad_f](t, a=q, b=b)
            self.d2R = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: \
                self.R0 * (1 - C) * d2f[rad_f](t, a=q, b=b)
            self.rad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.rad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.drad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.drad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.d2rad_x = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
            self.d2rad_y = lambda t, C=rad_curve['C'], q=rad_curve['q'], b=rad_curve['b']: 0
        f['rad_x'], f['rad_y'] = self.rad_x, self.rad_y
        df['rad_x'], df['rad_y'] = self.drad_x, self.drad_y
        d2f['rad_x'], d2f['rad_y'] = self.d2rad_x, self.d2rad_y
        f['rad'], df['rad'], d2f['rad'] = self.R, self.dR, self.d2R
        s, pow, exp = 0, 2.2, 2
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
        self.d2x = lambda t, scale=r_scale: self.d2R(t) * (
                self.base_x(t) + 1 / scale * self.curls_x(t) + s / scale ** pow * self.curls_x(-t, a=speed * (
                speed ** (exp - 1)))) + 2 * self.dR(t) * (self.dbase_x(t) + 1 / scale * self.dcurls_x(
            t) + s / scale ** pow * self.dcurls_x(-t, a=speed * (speed ** (exp - 1)))) + self.R(t) * (
                                                    self.d2base_x(t) + 1 / scale * self.d2curls_x(
                                                t) + s / scale ** pow * self.d2curls_x(-t, a=speed * (
                                                    speed ** (exp - 1)))) + self.d2rad_x(t)
        self.d2y = lambda t, scale=r_scale: self.d2R(t) * (
                self.base_y(t) + 1 / scale * self.curls_y(t) + s / scale ** pow * self.curls_y(-t, c=speed * (
                speed ** (exp - 1)))) + 2 * self.dR(t) * (self.dbase_y(t) + 1 / scale * self.dcurls_y(
            t) + s / scale ** pow * self.dcurls_y(-t, c=speed * round(speed ** (exp - 1)))) + self.R(t) * (
                                                    self.d2base_y(t) + 1 / scale * self.d2curls_y(
                                                t) + s / scale ** pow * self.d2curls_y(-t, c=speed * round(
                                                speed ** (exp - 1)))) + self.d2rad_y(t)
        f['x'], f['y'] = self.x, self.y
        df['x'], df['y'] = self.dx, self.dy
        d2f['x'], d2f['y'] = self.d2x, self.d2y
        # print(base_x, base_y, curls_x, curls_y, speed, r_scale)
        # some other derivatives for colouring
        df['(base+curls)_x'] = lambda t: self.dx(t) - self.drad_x(t)
        df['(base+curls)_y'] = lambda t: self.dy(t) - self.drad_y(t)
        df['(base+rad)_x'] = lambda t: self.dR(t) * self.base_x(t) + self.R(t) * self.dbase_x(t) + \
                                       self.drad_x(t)
        df['(base+rad)_y'] = lambda t: self.dR(t) * self.base_y(t) + self.R(t) * self.dbase_y(t) + \
                                       self.drad_y(t)

        self.phi = lambda t, dx=self.dx, dy=self.dy: np.sign(dy(t)) * np.arccos(
            dx(t) / np.sqrt(dx(t) ** 2 + dy(t) ** 2))

        for func in df.keys():
            f['d' + func] = df[func]
        for func in d2f.keys():
            f['d2' + func] = d2f[func]

        self.t = 0.0
        self.step_count = 0
        self.perimeter = 0
        self.av = 1
        # self.draw_rate = 0.03  # 31 * pi / 41  # 6 * 1e-2
        self.rate = 3 * min(0.08 / speed, 0.06)
        nums = (2, max(rad_curve['q'], max(1, s * speed ** exp)), base_curve['a'], base_curve['c'], curls['a'] * speed,
                curls['c'] * speed)
        self.per = np.abs(get_period(2, max(rad_curve['q'], max(1, s * speed ** exp)), base_curve['a'], base_curve['c'],
                                     curls['a'] * speed, curls['c'] * speed))
        if self.per % 1 == 0:
            self.per = round(self.per)
        print(f'A periódus: {self.per}pi', nums)

        a, b = 0, self.per * pi
        b = int(round(b + 0.5))
        if b - a > 10 ** 3:
            T = np.linspace(a, a + 10 ** 3, 10 ** 4 + 1)
        else:
            T = np.linspace(a, b, 10 * (b - a) + 1)
        funcs = []
        pref = 'd'
        for g in f.keys():
            if g[:len(pref)] == pref and g[-1] == 'x':
                funcs += [g[:-1]]
        max_norm = {g: 0 for g in funcs}
        av_norm = {g: 0 for g in funcs}
        self.max_diff = {}
        self.av_diff = {}
        xmax, xmin = 0, self.width
        ymax, ymin = 0, self.height
        for t in T:
            xmax, xmin = max(xmax, f['x'](t)), min(xmin, f['x'](t))
            ymax, ymin = max(ymax, f['y'](t)), min(ymin, f['y'](t))
            for g in funcs:
                n = np.sqrt(f[g + 'x'](t) ** 2 + f[g + 'y'](t) ** 2)
                max_norm[g] = max(max_norm[g], n)
                av_norm[g] += n
        for g in max_norm.keys():
            self.max_diff[g + 'x', g + 'y'] = max_norm[g]
            self.av_diff[g + 'x', g + 'y'] = av_norm[g] / len(T)
        print(self.max_diff.keys())
        for key, val in self.max_diff.items():
            print(f'{key}: {val:.2f}, {self.av_diff[key]:.2f}')
        self.max_norm = max_norm
        # self.max_slope, self.av_slope, T = get_max(self.dx, self.dy, 0, self.per * pi)
        # print(round(self.max_slope, 2), round(self.av_slope, 2))
        # xmax = max([self.x(t) for t in T])
        # xmin = min([self.x(t) for t in T])
        # ymax = max([self.y(t) for t in T])
        # ymin = max([self.y(t) for t in T])
        M = max(xmax - self.width // 2, ymax - self.height // 2, self.width // 2 - xmin, self.height // 2 - ymin)
        rescale_factor = (min(self.width, self.height) // 2 - 50) / M
        self.R0 *= rescale_factor
        self.r0 *= rescale_factor
        # self.max_base_slope, self.av_base_slope, _ = get_max(self.dbase_x, self.dbase_y, 0, get_period(base_curve['a'], base_curve['c']))
        # self.max_curls_slope, self.av_curls_slope, _ = get_max(self.dcurls_x, self.dcurls_y, 0, round(
        #     get_period(curls['a'], curls['c']) * speed) * pi)
        # self.max_diff['x', 'y'] = self.max_slope
        # self.max_diff['base_x', 'base_y'] = self.max_base_slope
        # self.max_diff['curls_x', 'curls_y'] = self.max_curls_slope
        # self.max_diff['curls_x', 'curls_y'] = self.max_curls_slope
        # self.max_diff['(base+curls)_x', '(base+curls)_y'] = max(self.max_base_slope, self.max_curls_slope,
        #                                                         self.max_slope)
        # if ORTHOGONAL_WAVES:
        # self.max_rad_slope, self.av_rad_slope, _ = get_max(self.drad_x, self.drad_y, 0, rad_curve['q'] * pi)
        # self.max_diff['rad_x', 'rad_y'] = self.max_rad_slope
        # self.max_diff['(base+rad)_x', '(base+rad)_y'] = max(self.max_base_slope, self.max_rad_slope)

    def update(self, x='x', y='y', pref='d'):
        global f
        target = 10
        self.step_count += 1
        x0, y0 = f[x](self.t), f[y](self.t)
        if self.ADAPTIVE_RATE:
            px, py = pref + x, pref + y
            # delta = min(1, 2 * np.sqrt(f[px](self.t) ** 2 + f[py](self.t) ** 2) /
            #             (self.max_diff[px, py] + self.av_diff[px, py]))
            delta = np.sqrt(f[px](self.t) ** 2 + f[py](self.t) ** 2) / (self.max_diff[px, py]) ** 1.5
            # delta = delta ** 0.5
            if delta >= 1:
                print(f'{self.t:.2f}, {np.sqrt(f[px](self.t) ** 2 + f[py](self.t) ** 2):.2f}')
            # delta = (delta ** 0.04) / max(np.power(self.per, 0.8), 100)  # 100
            # print(round(delta, 3))
            # while np.abs((self.phi(self.t + delta, dx=f[px], dy=f[py]) - self.phi(self.t, dx=f[px], dy=f[py]))) % (
            #         2 * pi) > 0.05 * pi:
            #     # print(f'{delta}, {self.phi(self.t + delta, dx=f[px], dy=f[py]) - self.phi(self.t, dx=f[px], dy=f[py]):.2f}')
            #     delta /= 2
            self.t += delta * self.av  # /100# * self.av  # + self.t / (self.av * self.step_count)
        else:
            self.t += self.rate
        if x + y == 'xy':
            x1, y1 = f[x](self.t), f[y](self.t)
            self.perimeter += np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            self.av = target * self.step_count / self.perimeter  # target * self.t / self.perimeter
        return f[x](self.t), f[y](self.t)

    def get_derivatives(self, t=None, x='x', y='y'):
        if t is None:
            t = self.t
        return df[x](t), df[y](t)

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
                points.append((f[x](t), f[y](t)))
                t += self.rate
                delta = (np.sqrt(df[x](t) ** 2 + df[y](t) ** 2) / self.max_diff[x, y])
                delta = (delta ** 0.04) / max(np.power(self.per, 0.7), 100)
                t += delta
        else:
            while t < limit:
                points.append((f[x](t), f[y](t)))
                t += self.rate
        return points
