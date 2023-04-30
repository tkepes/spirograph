import numpy as np
import sympy as sp

sin = lambda t, a=1, b=0: sp.sin(a * t + b)
cos = lambda t, a=1, b=0: sp.cos(a * t + b)
t = sp.symbols('t')


def euclidean(a, b):
    while a % b != 0:
        a, b = b, a % b
    return b


def base_curve():
    pass


class Spirograph:
    def __init__(self, width=2000, height=2000, ADAPTIVE_RATE=True, A=1, B=1, C=1, D=1, a=1, b=1, c=1, d=1, Tc=0, tc=0,
                 Ts=0, ts=0, **kwargs):
        self.width = width
        self.height = height
        self.ADAPTIVE_RATE = ADAPTIVE_RATE
        self.A, self.B, self.C, self.D = A, B, C, D
        self.a, self.b, self.c, self.d = a, b, c, d
        self.Tc, self.tc, self.Ts, self.ts = Tc, tc, Ts, ts

        sin = lambda t, a=1, b=0: sp.sin(a * t + b)
        cos = lambda t, a=1, b=0: sp.cos(a * t + b)
        dsin = lambda t, a=1, b=0: a * cos(t, a, b)
        dcos = lambda t, a=1, b=0: -a * sin(t, a, b)
        x_keys = ['COS', 'cos']
        y_keys = ['SIN', 'sin']
        ce = {'COS': 1, 'SIN': 1, 'cos': 1, 'sin': 1}
        fact = {'COS': 1, 'SIN': 1, 'cos': 1, 'sin': 1}
        shift = {'COS': 0, 'SIN': 0, 'cos': 0, 'sin': 0}
        rad_keys = ['R', 'r']

        self.r0 = 1 * self.width // 32  # 100
        self.R0 = min(self.width, self.height) // (2 * sp.sqrt(max(self.A, self.C))) - 120 - self.r0

        # self.x = self.width // 2 + self.R0 + self.r0
        # self.y = self.height // 2
        self.RC = 0.9
        self.q = 20
        self.R = lambda t: self.R0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dR = lambda t: self.R0 * (1 - self.RC) * dsin(t, a=self.q)
        self.r = lambda t: self.r0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dr = lambda t: self.r0 * (1 - self.RC) * dsin(t, a=self.q)
        func = {'COS': cos, 'SIN': sin, 'cos': cos, 'sin': sin, 'R': self.R, 'r': self.r}
        rad = {'COS': 'R', 'SIN': 'R', 'cos': 'r', 'sin': 'r'}
        dfunc = {'COS': dcos, 'SIN': dsin, 'cos': dcos, 'sin': dsin, 'R': self.dR, 'r': self.dr}
        self.x = lambda t: self.width // 2 + \
                           sum([func[rad[f]](t) * ce[f] * func[f](t, a=fact[f], b=shift[f]) for f in x_keys])
        self.dx = lambda t: sum([func[rad[f]](t) * ce[f] * dfunc[f](t, a=fact[f], b=shift[f]) +
                                 dfunc[rad[f]](t) * ce[f] * dfunc[f](t, a=fact[f], b=shift[f]) for f in x_keys])
        self.y = lambda t: self.height // 2 + \
                           sum([func[rad[f]](t) * ce[f] * func[f](t, a=fact[f], b=shift[f]) for f in y_keys])
        self.dy = lambda t: sum([func[rad[f]](t) * ce[f] * dfunc[f](t, a=fact[f], b=shift[f]) +
                                 dfunc[rad[f]](t) * ce[f] * dfunc[f](t, a=fact[f], b=shift[f]) for f in x_keys])
        # self.A = 2
        self.a = 4
        self.c = 3
        self.Tc = sp.pi / 2
        self.r0 = 1 * self.width // 32  # 100
        self.R0 = min(self.width, self.height) // (2 * sp.sqrt(max(self.A, self.C))) - 120 - self.r0

        # self.x = self.width // 2 + self.R0 + self.r0
        # self.y = self.height // 2
        self.q = 20  # 6
        self.speed = 20.05  # 20.05  # 15.12  # 1.02
        self.RC = 0.9
        self.R = lambda t: self.R0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.r = lambda t: self.r0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dR = lambda t: self.R0 * (1 - self.RC) * dsin(t, a=self.q)
        self.r = lambda t: self.r0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dr = lambda t: self.r0 * (1 - self.RC) * dsin(t, a=self.q)
        self.r2 = lambda t: 0 * self.r0 ** 3 / self.R0 ** 2 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)
        self.dr2 = lambda t: 0 * self.r0 ** 3 / self.R0 ** 2 * (1 - self.RC) * dsin(t, a=self.q)
        k = 0
        self.x = lambda t: self.width // 2 + self.A * self.R(t) * cos(t, a=self.a, b=self.Tc) + \
                           self.B * self.r(t) * cos(t, a=self.b * self.speed, b=self.tc) + \
                           self.r2(t) * cos(t, a=self.b * self.speed ** 4) + k * self.r0 * (
                                   0 * sin(t, a=12) + cos(t, a=12))
        t = sp.symbols('t')
        # print(self.R0)
        # print(self.r0)
        # print(self.R(t))
        # print(self.r(t))
        print(self.x(t))
        print(sp.diff(self.x(t)))
        self.dx = lambda t: self.A * (self.dR(t) * cos(t, a=self.a, b=self.Tc) +
                                      self.R(t) * dcos(t, a=self.a, b=self.Tc)) + \
                            self.B * (self.dr(t) * cos(t, a=self.b * self.speed, b=self.tc) +
                                      self.r(t) * dcos(t, a=self.b * self.speed, b=self.tc)) + \
                            self.r2(t) * dcos(t, a=self.b * self.speed ** 4) + \
                            self.dr2(t) * cos(t, a=self.b * self.speed ** 4)
        self.y = lambda t: self.height // 2 + self.C * self.R(t) * sin(t, self.c, b=self.Ts) - \
                           self.D * self.r(t) * sin(t, a=self.d * self.speed, b=self.ts) + \
                           self.r2(t) * cos(t, a=self.d * self.speed ** 4) + k * self.r0 * (
                                   sin(t, a=12) + 0 * cos(t, a=12))
        self.dy = lambda t: self.C * (self.dR(t) * sin(t, a=self.c, b=self.Ts) +
                                      self.R(t) * dsin(t, a=self.c, b=self.Ts)) - \
                            self.D * (self.dr(t) * sin(t, a=self.d * self.speed, b=self.ts) +
                                      self.r(t) * dsin(t, a=self.d * self.speed, b=self.ts)) + \
                            self.r2(t) * dsin(t, a=self.d * self.speed ** 4) + \
                            self.dr2(t) * sin(t, a=self.d * self.speed ** 4)

        # self.r0 = 1 * self.width // 32  # 100
        # self.R0 = min(self.width, self.height) // (2 * np.sqrt(max(self.A, self.C))) - 120 - self.r0
        # self.q = 20  # 6
        # self.RC = 0.9
        # self.R = lambda t: self.R0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)  # R*sin(qt)
        # self.r = lambda t: self.r0 * ((1 - self.RC) * sin(t, a=self.q) + self.RC)  # r*sin(qt)
        # self.speed = 6.05
        # self.a = 4
        # self.c = 3
        # self.Tc = np.pi / 2
        # # self.A = 2
        # # x(t) = A * R * cos(at + Tc) + r * cos(speed t)
        # # y(t) = R * sin(ct + Ts) - r * cos(speed t)
        # self.x = lambda t: self.width // 2 + self.A * self.R(t) * cos(self.a * t + self.Tc) + self.r(t) * cos(
        #     self.speed * t)
        # self.y = lambda t: self.height // 2 + self.R(t) * sin(self.c * t + self.Ts) - self.r(t) * sin(self.speed * t)

        self.phi = lambda t: np.sign(self.dy(t)) * np.arccos(self.dx(t) / np.sqrt(self.dx(t) ** 2 + self.dy(t) ** 2))
        # self.x1 = lambda t: self.x(t) +
        self.t = 0.0
        # self.rate = 0.03  # 31 * np.pi / 41  # 6 * 1e-2
        self.rate = 3 * min(0.08 / self.speed, 0.06)

        # self.x, self.y = self.update()
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

        self.per = np.abs(get_period(max(self.q, 1), self.a, self.b * self.speed, self.c, self.d * self.speed))
        print(self.q, self.a, self.b * self.speed, self.c, self.d * self.speed)
        print(self.per)
        if self.per > 10 ** 3:
            m = round(max(self.q, self.a, self.b * self.speed, self.c, self.d * self.speed))
            T = np.linspace(0, m, 10 * m + 1)
        else:
            T = np.linspace(0, self.per, 10 * self.per + 1)
        maxx = max([self.x(t) for t in T])
        minx = min([self.x(t) for t in T])
        maxy = max([self.y(t) for t in T])
        miny = max([self.y(t) for t in T])
        max_ = max(maxx - self.width // 2, maxy - self.height // 2, self.width // 2 - minx, self.height // 2 - miny)
        m = (min(self.width, self.height) // 2 - 120) / max_
        self.R0 *= m
        self.r0 *= m
        dF = [(round(self.dx(t)), round(self.dy(t))) for t in T]  # np.linspace(0, self.per, 10 * self.per + 1)]
        D = [sp.sqrt(dx ** 2 + dy ** 2) for dx, dy in dF]
        self.maxslope = float(max(D))
        self.avslope = sum(D) / len(D)  # .average(D)
        print(round(self.maxslope, 2), round(self.avslope, 2))

    def coordinate_functions(self, cos_fact, cos_const, sin_fact, sin_const):
        return lambda t: np.cos(cos_fact * t + cos_const), lambda t: np.sin(sin_fact * t + sin_const)

    def update(self):
        # self.x = self.width // 2 + self.A * self.R0 * (0.5 * np.sin(3 * self.t) + 0.5) * np.cos(
        #     self.a * self.t + self.Tc) + self.B * self.r0 * np.cos(self.b * self.speed * self.t + self.tc)
        # self.y = self.height // 2 + self.C * self.R0 * (0.5 * np.sin(3 * self.t) + 0.5) * np.sin(
        #     self.c * self.t + self.Ts) - self.D * self.r0 * np.sin(self.d * self.speed * self.t + self.ts)
        # np.sin(self.speed * self.t)
        if self.ADAPTIVE_RATE:
            delta = (sp.sqrt(self.dx(self.t) ** 2 + self.dy(self.t) ** 2) / self.maxslope)
            delta = (delta ** 0.05) / 100  # 100
            # print(round(delta, 3))
            self.t += delta
        else:
            self.t += self.rate
        return float(self.x(self.t)), float(self.y(self.t))

    def get_derivatives(self):
        # dx = -self.a * self.A * self.R0 * np.sin(self.a * self.t + self.Tc) - \
        #      self.b * self.speed * self.B * self.r0 * np.sin(self.b * self.speed * self.t + self.tc)
        # dy = self.c * self.C * self.R0 * np.cos(self.c * self.t + self.Ts) - \
        #      self.d * self.speed * self.D * self.r0 * np.cos(self.d * self.speed * self.t + self.ts)
        # return dx, dy
        return float(self.dx(self.t)), float(self.dy(self.t))

    def get_params(self):
        return self.A, self.B, self.C, self.D, self.a, self.b, self.c, self.d, self.Tc, self.Ts, self.tc, self.ts
