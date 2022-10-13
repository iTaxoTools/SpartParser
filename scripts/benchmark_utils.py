from time import perf_counter
from os import getpid
from os.path import getsize
from psutil import Process


class Timer:

    def __init__(self, id, msg=None):
        self.id = id
        self.msg = msg or 'Tick {}: {:.4f}s'

    def __enter__(self):
        self.t = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        s = perf_counter() - self.t
        print(self.msg.format(self.id, s))


class LoopTimer:

    counters = dict()
    msg = 'Tock {}: {:.4f}s'

    def __init__(self, id):
        self.id = id
        if not id in self.counters:
            self.counters[id] = 0.0

    def __enter__(self):
        self.t = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        s = perf_counter() - self.t
        self.counters[self.id] += s

    @classmethod
    def print(cls, id, msg=None):
        t = cls.counters[id]
        msg = msg or cls.msg
        print(msg.format(id, t))


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def print_memory_usage():
    process = Process(getpid())
    bytes = process.memory_info().rss
    print(f'Memory used: {sizeof_fmt(bytes)}')


def print_file_size(path):
    bytes = getsize(path)
    print(f'File size: {sizeof_fmt(bytes)}')
