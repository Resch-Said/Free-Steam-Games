import os


class BetterPath:
    @classmethod
    def create_path(cls, path):
        if not os.path.exists(path):
            os.makedirs(path)

    @classmethod
    def get_absolute_path(cls, path):
        cls.create_path(path)
        return os.path.abspath(path)
