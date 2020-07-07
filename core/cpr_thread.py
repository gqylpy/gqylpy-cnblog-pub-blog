import threading


class GQYThread(threading.Thread):
    def __init__(self, fn, args: tuple, name: str = ''):
        threading.Thread.__init__(self)
