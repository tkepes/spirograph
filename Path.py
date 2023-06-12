import os
from datetime import datetime as dt


# def create_folder(directory):
#     try:
#         if not os.PATH.exists(directory):
#             os.makedirs(directory)
#     except OSError:
#         print('Error: Creating directory. ' + directory)


class Path:
    def __init__(self, path=''):
        self.path0 = path
        self.path = self.path0 + str(dt.today().date())
        self.create_folder()

    def create_folder(self, directory=''):
        directory = self.path + directory
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error creating directory: ' + directory)

    def __len__(self):
        return len(self.path)

    def instant(self):
        return str(dt.today().time())[:8].replace(':', '-')

    def update(self, name):
        self.path += '/' + name
        self.create_folder()

    def reset(self):
        self.path = self.path0 + str(dt.today().date())

    def __str__(self):
        return self.path

    def __radd__(self, other):
        return other + self.path

    def __add__(self, other):
        return self.path + other
