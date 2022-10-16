from sys import argv
from pathlib import Path

from itaxotools.spart_parser import Spart
from benchmark_utils import Timer

"""
Memory benchmark using memory_profiler & matplotlib:

    $ mprof run -C load_spart.py <input>
    $ mprof peak
    $ mprof plot

"""

path = Path(argv[1])

extension = path.suffix

parser = {
    '.xml': Spart.fromXML,
    '.spart': Spart.fromMatricial,
}[extension]


with Timer('load', 'Time to {}: {:.4f}s'):
    spart = parser(path)


input('Press ENTER to exit...')
