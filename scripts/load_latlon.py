from sys import argv
from pathlib import Path
import pandas as pd

from itaxotools.spart_parser import Spart
from benchmark_utils import Timer

"""
Memory benchmark using memory_profiler & matplotlib:

    $ mprof run -C load_spart.py <input>
    $ mprof peak
    $ mprof plot

"""

path = Path(argv[1])

extension = ''.join(path.suffixes)

parser = {
    '.xml': Spart.fromXML,
    '.dev.xml': Spart.fromXML_dev,
    '.spart': Spart.fromMatricial,
}[extension]


with Timer('load', 'Time to {}: {:.4f}s'):
    spart = parser(path)

with Timer('pandas', 'Time to {}: {:.4f}s'):
    data = {'id': [], 'lat': [], 'lon':[]}
    for id in spart.getIndividuals():
        lat, lon = spart.getIndividualLatlon(id)
        data['id'].append(id)
        data['lat'].append(lat)
        data['lon'].append(lon)

    f = pd.DataFrame(data)
    f = f.set_index('id')

# f.to_csv('dump.csv')

input('Press ENTER to exit...')
