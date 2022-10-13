from sys import argv
from pathlib import Path

from itaxotools.spart_parser import Spart
from benchmark_utils import Timer, print_memory_usage


path = Path(argv[1])

extension = path.suffix

parser = {
    '.xml': Spart.fromXML,
    '.spart': Spart.fromMatricial,
}[extension]

with Timer('load', 'Time to {}: {:.4f}s'):
    spart = parser(path)

print_memory_usage()
