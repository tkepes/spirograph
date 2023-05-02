import numpy as np
from numpy import pi as pi

sin = lambda t, a=1, b=0: np.sin(a * t + b)
cos = lambda t, a=1, b=0: np.cos(a * t + b)
dsin = lambda t, a=1, b=0: a * cos(t, a, b)
dcos = lambda t, a=1, b=0: -a * sin(t, a, b)
d2sin = lambda t, a=1, b=0: a * dcos(t, a, b)
d2cos = lambda t, a=1, b=0: -a * dsin(t, a, b)
zin = lambda t, a=1, b=0: 4 * min((a * t / pi / 2 + b) % 1, (-(a * t / pi / 2 + b)) % 1) - 1
coz = lambda t, a=1, b=0: zin(t, a=1, b=pi / 2 + b)
dzin = lambda t, a=1, b=0: 2 * a / pi * np.sign(1 / 2 - (a * t / pi / 2 + b) % 1)
dcoz = lambda t, a=1, b=0: dzin(t, a=1, b=pi / 2 + b)
d2zin = lambda t, a=1, b=0: 0
d2coz = lambda t, a=1, b=0: 0
f = {'sin': sin, 'cos': cos, 'zin': zin, 'coz': coz}
df = {'sin': dsin, 'cos': dcos, 'zin': dzin, 'coz': dcoz}
d2f = {'sin': d2sin, 'cos': d2cos, 'zin': d2zin, 'coz': d2coz}

norm0 = lambda t, x, y, p=2: np.power(x(t) ** p + y(t) ** p, 1 / p)
norm = lambda t, x, y, p=2: norm0(t, x, y, p) if norm0(t, x, y, p) != 0 else 1
normalise = lambda t, x, y, p=2: (x(t) / norm(t, x, y, p), y(t) / norm(t, x, y, p))
