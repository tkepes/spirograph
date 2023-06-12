from Path import Path
from Parameters import *
from MyFunctions import f


def get_curve_name(latex=False, rad_on=True, base_x=base_x, base_y=base_y, base_curve_coeffs=base_curve_coeffs,
                   curls_on=True, curls_x=curls_x, curls_y=curls_y, curls_curve_coeffs=curls_curve_coeffs,
                   radius_curve_coeffs=radius_curve_coeffs, speed=speed, q=q, rad_f=rad_f,
                   ORTHOGONAL_WAVES=ORTHOGONAL_WAVES, NORMALISE_WAVES=NORMALISE_WAVES, C=C):
    if latex:
        prod_char = ' \cdot '
        prod_char2 = '\cdot '
        pi_str = '\__pi'.replace('__', '')
    else:
        prod_char = ' '
        prod_char2 = ' '
        pi_str = 'pi'

    def str_mult(a, b, prod_char=' \cdot '):
        if not isinstance(b, str) and not isinstance(a, str):
            return a * b
        elif 0 in [a, b]:
            return 0
        else:
            if 1 in [a, b]:
                if a == 1:
                    a, b = b, a
                return a
            elif -1 in [a, b]:
                if a == -1:
                    a, b = b, a
                if a[0] == '-':
                    return a[1:]
                return f'-{a}'
        swapped = False
        if isinstance(a, str):
            a, b = b, a
            swapped = True
        if not isinstance(a, str):
            n = 4
            while n > 0 and a == round(a, n - 1):
                n -= 1
            if n == 0:
                a = str(round(a))
            else:
                a = str(round(a, n))
        if swapped:
            a, b = b, a
        return f'{a}{prod_char}{b}'

    def str_sign(expr):
        if not isinstance(expr, str):
            return expr >= 0
        return expr.strip()[0] != '-'

    def str_add(a, b):
        if not isinstance(a, str) and not isinstance(b, str):
            return a + b
        elif b == 0:
            return a
        elif a == 0:
            return b
        elif not str_sign(b):
            if not isinstance(b, str):
                return f'{a} - {-b}'
            return f'{a} - {b[1:]}'
        return f'{a} + {b}'

    def change_sign(expr):
        if not isinstance(expr, str):
            return -expr
        if expr.strip()[0] == '-':
            return expr[1:]
        return '-' + expr

    def func_val_calc(coeffs, A='A', a='a', b='b', ff=base_x):
        inner_prod_char = ''
        t = str_mult(coeffs[a], 't', inner_prod_char)
        if t == 0:
            t = coeffs[b]
            ff = f[ff](t)
        else:
            sign = str_sign(t)
            # print(t, sign, ff, str_mult((-1) ** (sign + 1) * round(coeffs[b] / pi, 2), pi_str), end=' ')
            t = str_add(t[1 - sign:], str_mult((-1) ** (sign + 1) * round(coeffs[b] / pi, 2), pi_str, inner_prod_char))
            # print(t)
            ff = f"{ff}({t})"
            if not sign and ff[:3] not in ['cos', 'coz']:
                return str_mult(change_sign(coeffs[A]), ff, prod_char=prod_char)
        return str_mult(coeffs[A], ff, prod_char=prod_char)

    # base_x_str = str_mult(base_curve_coeffs['A'], base_x + '('+ str_add(str_mult(base_curve_coeffs['a'], 't'), base_curve_coeffs['b'])+')')

    x_str = ''
    y_str = ''

    def latexify(expr='', curve_type='base'):
        if latex:
            # if not isinstance(expr, str):
            #     return expr
            if not str_sign(expr):
                expr = f'-$:{curve_cols[curve_type]}[${change_sign(expr)}$]$'
            else:
                expr = f'$:{curve_cols[curve_type]}[${expr}$]$'
        return expr

    base_x_str = func_val_calc(base_curve_coeffs, ff=base_x)
    base_y_str = func_val_calc(base_curve_coeffs, A='B', a='c', b='d', ff=base_y)
    base_x_str = latexify(base_x_str, curve_type='base')
    base_y_str = latexify(base_y_str, curve_type='base')
    if curls_on:
        curls_curve_coeffs2 = {key: (-curls_curve_coeffs[key] * speed if key in 'ac' else (
            curls_curve_coeffs[key] / rad_ratio if key in 'AB' else curls_curve_coeffs[key])) for key in
                               curls_curve_coeffs}
        # print(curls_curve_coeffs2)
        curls_x_str = func_val_calc(curls_curve_coeffs2, ff=curls_x)
        curls_y_str = func_val_calc(curls_curve_coeffs2, A='B', a='c', b='d', ff=curls_y)
        if latex:
            neg = not str_sign(curls_x_str)
            if not isinstance(curls_x_str, str):
                curls_curve_coeffs2['A'] = (-1) ** (neg) * curls_curve_coeffs['A']
                curls_x_str = func_val_calc(curls_curve_coeffs2, ff=curls_x)
                curls_x_str = ('-' if neg else '') + '\__frac{' + str(curls_x_str) + '}{' + str(rad_ratio) + '}'
            else:
                curls_curve_coeffs2['A'] = '\__frac{' + str(curls_curve_coeffs['A']) + '}{' + str(rad_ratio) + '}'
                curls_x_str = func_val_calc(curls_curve_coeffs2, ff=curls_x)
            neg = not str_sign(curls_y_str)
            if not isinstance(curls_y_str, str):
                curls_curve_coeffs2['B'] = (-1) ** (neg) * curls_curve_coeffs['B']
                curls_y_str = func_val_calc(curls_curve_coeffs2, A='B', a='c', b='d', ff=curls_y)
                curls_y_str = ('-' if neg else '') + '\__frac{' + str(curls_y_str) + '}{' + str(rad_ratio) + '}'
            else:
                curls_curve_coeffs2['B'] = '\__frac{' + str(curls_curve_coeffs['B']) + '}{' + str(rad_ratio) + '}'
                curls_y_str = func_val_calc(curls_curve_coeffs2, A='B', a='c', b='d', ff=curls_y)
        curls_x_str = latexify(curls_x_str, 'curls')
        curls_y_str = latexify(curls_y_str, 'curls')
        x_str = str_add(base_x_str, curls_x_str)
        y_str = str_add(base_y_str, curls_y_str)
    else:
        x_str = base_x_str
        y_str = base_y_str
    if not rad_on:
        return f'R {prod_char2}({x_str}; {y_str})'
    if ORTHOGONAL_WAVES:
        name = ' -- R(t, x(t), y(t)) = R(x(t) + r_x(t), y(t) + r_y(t))'
        my_coeffs = {key: base_curve_coeffs[key] for key in base_curve_coeffs.keys()}
        my_coeffs['A'] = -(1 - C) * base_curve_coeffs['A'] * base_curve_coeffs['a'] ** 2
        my_coeffs['B'] = (1 - C) * base_curve_coeffs['B'] * base_curve_coeffs['c'] ** 2
        my_coeffs['q'] = q
        my_coeffs['rad_b'] = radius_curve_coeffs['b']
        my_coeffs['rx'] = func_val_calc(my_coeffs, ff=base_x)
        my_coeffs['ry'] = func_val_calc(my_coeffs, A='B', a='c', b='d', ff=base_y)
        rad_x_str = func_val_calc(my_coeffs, A='rx', a='q', b='rad_b', ff=rad_f)
        if rad_x_str != 0:
            rad_x_str = ('normed({})' if NORMALISE_WAVES else '{}').format(rad_x_str)
            # + (' div sqrt(square(d_2 base_x) + square(d_2 base_y))' if NORMALISE_WAVES else '')
            rad_x_str = latexify(rad_x_str, 'rad')
        rad_y_str = func_val_calc(my_coeffs, A='ry', a='q', b='rad_b', ff=rad_f)
        if rad_y_str != 0:
            rad_y_str = ('normed({})' if NORMALISE_WAVES else '{}').format(rad_y_str)
            # + (' div sqrt(square(d_2 base_x) + square(d_2 base_y))' if NORMALISE_WAVES else '')
            rad_y_str = latexify(rad_y_str, 'rad')
        x_str = str_add(x_str, rad_x_str)
        y_str = str_add(y_str, rad_y_str)
        rad_f_str = 'R'  # str(round(R))
    else:
        name = ' -- R(t, x(t), y(t)) = R(t)(x(t), y(t))'
        my_coeffs = {'A': (1 - C), 'q': q, 'b': radius_curve_coeffs['b']}
        rad_f_str = str_add(func_val_calc(my_coeffs, a="q", ff=rad_f), C)
        rad_f_str = latexify(rad_f_str, 'rad')
        if isinstance(rad_f_str, str):
            rad_f_str = f'R{prod_char}({rad_f_str})'
        else:
            rad_f_str = f'{rad_f_str}R'
        # str_mult(round(R),  f'({str_add(func_val_calc(my_coeffs, a="q", ff=rad_f), C)})')
    name = f'{rad_f_str} {prod_char2}({x_str}, {y_str})'  # + name
    if latex:
        name = name.replace(', ', '; \quad ').replace('__', '')
        name = '$' + name + '$'
        # name = name.replace('(', '\left(')
        # name = name.replace(')', '\__right)').replace('__', '')
    while '  ' in name:
        print('double space', name.index('  '), name)
        name = name.replace('  ', ' ')
    return name


class Name:
    def __init__(self, path=None):
        if path is not None:
            self.PATH = path
        else:
            self.PATH = Path()

    def get_name(self, name=None, stage=0, final_save=False):
        if name is None:
            name = ''
        stage += 1
        stage_len = len(str(stage))
        if name == 'temp':
            name = 'Images/temp.png'
            # if self.st_res:
            #     self.st_im.save('Images/temp_st.png')
            stage -= 1
        elif final_save and stage == 1:
            name = self.PATH + '/' + self.PATH.instant() + ' ' + name + '.png'
        else:
            if not final_save:
                'Images/temp.png'
                'Images/temp_st.png'
            if len(self.PATH) == 17:
                path = self.PATH.instant() + ' - ' + name
                self.PATH.update(path)
            name = self.PATH + '/' + '000'[:3 - stage_len] + str(stage) + ' ' + self.PATH.instant() + '.png'
        return name, stage
