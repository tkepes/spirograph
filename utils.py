import os


def euclidean(a, b):
    while a % b != 0:
        a, b = b, a % b
    return b


def parameters_string(spirog):
    # x = A * R0 * cos(at) + B * r0 * cos(bwt)
    # y = C * R0 * sin(ct) - D * r0 * sin(dwt)
    # speed = w
    # rate = t_{n+1} - t_n
    st = 'r0 div R0 = {:.2f}, q = {}, rate = {:.2f}, speed = {:.2f}'.format(spirog.r0 / spirog.R0, spirog.q,
                                                                            spirog.rate, spirog.speed)
    args = spirog.get_params()
    for i in range(8):
        if args[i] != 1:
            st += ', ' + 'ABCDabcd'[i] + ' = {:.2f}'.format(args[i])
    for i in range(4):
        if args[i + 8] != 1:
            st += ', ' + 'Tt'[i // 2] + 'cs'[i % 2] + ' = {}'.format(args[i])
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
