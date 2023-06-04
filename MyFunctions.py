import numpy as np
from numpy import pi as pi

sin = lambda t, a=1, b=0: np.sin(a * t + b)
cos = lambda t, a=1, b=0: np.cos(a * t + b)
dsin = lambda t, a=1, b=0: a * cos(t, a, b)
dcos = lambda t, a=1, b=0: -a * sin(t, a, b)
d2sin = lambda t, a=1, b=0: a * dcos(t, a, b)
d2cos = lambda t, a=1, b=0: -a * dsin(t, a, b)
pi_transf = lambda t, a=1, b=0: (a * t + b) / (2 * pi) + 1 / 4
dpi_transf = lambda t, a=1, b=0: a / (2 * pi)
d2pi_transf = lambda t, a=1, b=0: 0
zigzag = lambda t: min(t % 1, 1 - t % 1)
dzigzag = lambda t: np.sign(1 / 2 - t % 1)
d2zigzag = lambda t: 0
zin = lambda t, a=1, b=0: 4 * zigzag(pi_transf(t, a, b)) - 1
coz = lambda t, a=1, b=0: zin(t, a=a, b=pi / 2 + b)
dzin = lambda t, a=1, b=0: 4 * dpi_transf(t, a, b) * dzigzag(pi_transf(t, a, b))
dcoz = lambda t, a=1, b=0: dzin(t, a=a, b=pi / 2 + b)
d2zin = lambda t, a=1, b=0: 0
d2coz = lambda t, a=1, b=0: 0
sigmoid = lambda t: 1 / (1 + np.exp(-t))

f = {'sin': sin, 'cos': cos, 'zin': zin, 'coz': coz}
df = {'sin': dsin, 'cos': dcos, 'zin': dzin, 'coz': dcoz}
d2f = {'sin': d2sin, 'cos': d2cos, 'zin': d2zin, 'coz': d2coz}
d3f = {'sin': lambda t, a=1, b=0: -a ** 3 * cos(t, a, b),
       'cos': lambda t, a=1, b=0: a ** 3 * sin(t, a, b),
       'zin': d2zin, 'coz': d2coz}
for g in df:
    f['d' + g] = df[g]
for g in d2f:
    f['d2' + g] = d2f[g]
dicts = [f, df, d2f]
funcs = {(i, key): dicts[i][key] for i in range(len(dicts)) for key in dicts[i]}

norm0 = lambda t, x, y, p=2: np.power(x(t) ** p + y(t) ** p, 1 / p)
norm = lambda t, x, y, p=2: norm0(t, x, y, p) if norm0(t, x, y, p) != 0 else 1
normalise = lambda t, x, y, p=2: (x(t) / norm(t, x, y, p), y(t) / norm(t, x, y, p))
"""
['sin', 'cos', 'zin', 'coz', 'dsin', 'dcos', 'dzin', 'dcoz', 'd2sin', 'd2cos', 'd2zin', 'd2coz', 'base_x', 'base_y',
 'curls_x', 'curls_y', 'rad_x', 'rad_y', 'rad', 'x', 'y', 'dbase_x', 'dbase_y', 'dcurls_x', 'dcurls_y', 'drad_x',
 'drad_y', 'drad', 'dx', 'dy', 'd(base+curls)_x', 'd(base+curls)_y', 'd(base+rad)_x', 'd(base+rad)_y', 'd2base_x',
 'd2base_y', 'd2curls_x', 'd2curls_y', 'd2rad_x', 'd2rad_y', 'd2rad', 'd2x', 'd2y']
"""


class Func:
    def __init__(self, f=sin, name='', a: int = 1, b: float = 0.):
        self.f = f
        self.name = name
        self.a = a
        if len(str(b)) > 1 and str(b)[-2:] == '.0':
            b = round(b)
        self.b = b
        st = ''
        if self.a != 0:
            if self.a != 1:
                st = f'{self.a}t'
            else:
                st = 't'
        if self.b != 0:
            if self.b < 0:
                if st != '':
                    st += ' '
                st += f'- {-self.b}'
            else:
                if st == '':
                    st = str(self.b)
                else:
                    st += f' + {self.b}'
        self.name += f'({st})'

    def __str__(self):
        return self.name


def print_(name='', a: int = 1, b: float = 0.):
    if len(str(b)) > 1 and str(b)[-2:] == '.0':
        b = round(b)
    st = ''
    if a != 0:
        if a != 1:
            st = f'{a}t'
        else:
            st = 't'
    if b != 0:
        if b < 0:
            if st != '':
                st += ' '
            st += f'- {-b}'
        else:
            if st == '':
                st = str(b)
            else:
                st += f' + {b}'
    name += f'({st})'
