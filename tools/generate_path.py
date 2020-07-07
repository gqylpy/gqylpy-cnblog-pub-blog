import os


def gen_path(*args: str) -> str:
    # Generate an absolute path.
    return os.path.abspath(os.path.join(*args))
