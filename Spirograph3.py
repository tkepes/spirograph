import numpy as np
from utils import least_multiple_of, get_period


def get_max(f, g, a, b):
    if b - a > 10 ** 3:
        T = np.linspace(a, a + 10 ** 3, 10 ** 4 + 1)
    else:
        T = np.linspace(a, b, 10 * (b - a) + 1)
    D = [np.sqrt(f(t) ** 2 + g(t) ** 2) for t in T]
    return np.max(D), np.average(D), T


class Spirograph:
    def __init__(self, width=2000, height=2000, ADAPTIVE_RATE=True, base_curve=None, ribbon_curve=None,
                 radius_curve=None, **kwargs):
        self.width = width
        self.height = height
        self.ADAPTIVE_RATE = ADAPTIVE_RATE

        sin = lambda t, a=1, b=0: np.sin(a * t + b)
        cos = lambda t, a=1, b=0: np.cos(a * t + b)
        dsin = lambda t, a=1, b=0: a * cos(t, a, b)
        dcos = lambda t, a=1, b=0: -a * sin(t, a, b)
        print(ribbon_curve.keys())
        r_scale = ribbon_curve['R:r']
        speed = ribbon_curve['speed']
        self.R0 = min(self.width, self.height) // 2 / (1 + 1 / r_scale)
        self.r0 = self.R0 / r_scale
        self.x0 = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * cos(t, a=a, b=b)
        self.y0 = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: B * sin(t, a=c, b=d)
        self.dx0 = lambda t, A=base_curve['A'], a=base_curve['a'], b=base_curve['b']: A * dcos(t, a=a, b=b)
        self.dy0 = lambda t, B=base_curve['B'], c=base_curve['c'], d=base_curve['d']: B * dsin(t, a=c, b=d)
        # self.y0 = lambda t: base_curve['B'] * sin(t, a=base_curve['c'], b=base_curve['d'])
        # self.x1 = lambda t: ribbon_curve['A'] * cos(t, a=ribbon_curve['a'], b=ribbon_curve['b'])
        # self.y1 = lambda t: ribbon_curve['B'] * sin(t, a=ribbon_curve['c'], b=ribbon_curve['d'])
        self.x1 = lambda t, A=ribbon_curve['A'], a=ribbon_curve['a'], b=ribbon_curve['b']: A * cos(t, a=a * speed, b=b)
        self.y1 = lambda t, B=ribbon_curve['B'], c=ribbon_curve['c'], d=ribbon_curve['d']: B * sin(t, a=c * speed, b=d)
        self.dx1 = lambda t, A=ribbon_curve['A'], a=ribbon_curve['a'], b=ribbon_curve['b']: A * dcos(t, a=a * speed,
                                                                                                     b=b)
        self.dy1 = lambda t, B=ribbon_curve['B'], c=ribbon_curve['c'], d=ribbon_curve['d']: B * dsin(t, a=c * speed,
                                                                                                     b=d)
        # self.R = lambda t: radius_curve['R'] * \
        #                    ((1 - radius_curve['C']) * sin(t, a=radius_curve['q'], b=radius_curve['b']) + radius_curve[
        #                        'C'])
        self.R = lambda t, C=radius_curve['C'], q=radius_curve['q'], b=radius_curve['b']: \
            self.R0 * ((1 - C) * sin(t, a=q, b=b) + C)
        self.dR = lambda t, C=radius_curve['C'], q=radius_curve['q'], b=radius_curve['b']: \
            self.R0 * (1 - C) * dsin(t, a=q, b=b)
        self.x = lambda t, scale=r_scale: self.width // 2 + self.R(t) * (self.x0(t) + 1 / scale * self.x1(t))
        self.y = lambda t, scale=r_scale: self.height // 2 + self.R(t) * (self.y0(t) + 1 / scale * self.y1(t))
        self.dx = lambda t, scale=r_scale: self.dR(t) * (self.x0(t) + 1 / scale * self.x1(t)) + \
                                           self.R(t) * (self.dx0(t) + 1 / scale * self.dx1(t))
        self.dy = lambda t, scale=r_scale: self.dR(t) * (self.y0(t) + 1 / scale * self.y1(t)) + \
                                           self.R(t) * (self.dy0(t) + 1 / scale * self.dy1(t))

        self.phi = lambda t: np.sign(self.dy(t)) * np.arccos(self.dx(t) / np.sqrt(self.dx(t) ** 2 + self.dy(t) ** 2))
        # self.x1 = lambda t: self.x(t) +
        self.t = 0.0
        # self.rate = 0.03  # 31 * np.pi / 41  # 6 * 1e-2
        self.rate = 3 * min(0.08 / speed, 0.06)
        nums = (max(radius_curve['q'], 1), base_curve['a'], ribbon_curve['a'] * speed, base_curve['c'],
                ribbon_curve['c'] * speed)
        self.per = np.abs(
            least_multiple_of(max(radius_curve['q'], 1), base_curve['a'], ribbon_curve['a'] * speed, base_curve['c'],
                              ribbon_curve['c'] * speed))
        if self.per != np.abs(
                get_period(max(radius_curve['q'], 1), base_curve['a'], ribbon_curve['a'] * speed, base_curve['c'],
                           ribbon_curve['c'] * speed)):
            print(self.per, np.abs(
                get_period(max(radius_curve['q'], 1), base_curve['a'], ribbon_curve['a'] * speed, base_curve['c'],
                           ribbon_curve['c'] * speed)))
            print(nums)

        self.max_slope, self.av_slope, T = get_max(self.dx, self.dy, 0, self.per)
        print(round(self.max_slope, 2), round(self.av_slope, 2))
        xmax = max([self.x(t) for t in T])
        xmin = min([self.x(t) for t in T])
        ymax = max([self.y(t) for t in T])
        ymin = max([self.y(t) for t in T])
        M = max(xmax - self.width // 2, ymax - self.height // 2, self.width // 2 - xmin, self.height // 2 - ymin)
        rescale_factor = (min(self.width, self.height) // 2 - 120) / M
        self.R0 *= rescale_factor
        self.r0 *= rescale_factor
        self.max_base_slope, self.av_base_slope, _ = get_max(self.dx0, self.dy0, 0,
                                                             least_multiple_of(base_curve['a'], base_curve['c']))
        self.max_ribbon_slope, self.av_ribbon_slope, _ = get_max(self.dx1, self.dy1, 0, round(
            least_multiple_of(ribbon_curve['a'], ribbon_curve['c']) * speed))

    def update(self):
        # self.x = self.width // 2 + self.A * self.R0 * (0.5 * np.sin(3 * self.t) + 0.5) * np.cos(
        #     self.a * self.t + self.Tc) + self.B * self.r0 * np.cos(self.b * self.speed * self.t + self.tc)
        # self.y = self.height // 2 + self.C * self.R0 * (0.5 * np.sin(3 * self.t) + 0.5) * np.sin(
        #     self.c * self.t + self.Ts) - self.D * self.r0 * np.sin(self.d * self.speed * self.t + self.ts)
        # np.sin(self.speed * self.t)
        if self.ADAPTIVE_RATE:
            delta = (np.sqrt(self.dx(self.t) ** 2 + self.dy(self.t) ** 2) / self.max_slope)
            delta = (delta ** 0.05) / 100  # 100
            # print(round(delta, 3))
            self.t += delta
        else:
            self.t += self.rate
        return float(self.x(self.t)), float(self.y(self.t))

    def get_derivatives(self, type=''):
        # dx = -self.a * self.A * self.R0 * np.sin(self.a * self.t + self.Tc) - \
        #      self.b * self.speed * self.B * self.r0 * np.sin(self.b * self.speed * self.t + self.tc)
        # dy = self.c * self.C * self.R0 * np.cos(self.c * self.t + self.Ts) - \
        #      self.d * self.speed * self.D * self.r0 * np.cos(self.d * self.speed * self.t + self.ts)
        # return dx, dy
        if type == 'base':
            return self.dx0(self.t), self.dy0(self.t)
        elif type == 'ribbon':
            return self.dx1(self.t), self.dy1(self.t)
        return self.dx(self.t), self.dy(self.t)

    def get_base_derivatives(self):
        return self.dx0(self.t), self.dy0(self.t)

    def get_ribbon_derivatives(self):
        return self.dx1(self.t), self.dy1(self.t)

    def get_max_diff(self, type=''):
        if type == 'base':
            return self.max_base_slope
        elif type == 'ribbon':
            return self.max_ribbon_slope
        return self.max_slope
