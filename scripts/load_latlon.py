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

input = Path(argv[1])
output = Path(argv[2])

extension = ''.join(input.suffixes)

parser = {
    '.xml': Spart.fromXML,
    '.spart': Spart.fromMatricial,
}[extension]


with Timer('load', 'Time to {}: {:.4f}s'):
    spart = parser(input)

with Timer('pandas', 'Time to {}: {:.4f}s'):
    data = {'id': [], 'lat': [], 'lon':[]}
    for id in spart.getIndividuals():
        lat, lon = spart.getIndividualLatLon(id)
        data['id'].append(id)
        data['lat'].append(lat)
        data['lon'].append(lon)

    df = pd.DataFrame(data)
    df = df.set_index('id')

df.to_csv(output)
