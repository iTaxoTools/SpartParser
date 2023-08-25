from sys import argv, stdout
from pathlib import Path
import pandas as pd

from itaxotools.spart_parser import Spart


def print_tree(spart):
    for spartition in spart.getSpartitions():
        data = [f'{k}="{v}"' for k, v in spart.getSpartitionData(spartition).items()]
        print(f'<{spartition}>', *data)
        for subset in spart.getSpartitionSubsets(spartition):
            print('|')
            data = [f'{k}="{v}"' for k, v in spart.getSubsetData(spartition, subset).items()]
            print('+', f'<{subset}>', *data)
            for individual in spart.getSubsetIndividuals(spartition, subset):
                data = [f'{k}="{v}"' for k, v in spart.getIndividualData(individual).items()]
                data += [f'{k}="{v}"' for k, v in spart.getSubsetIndividualData(spartition, subset, individual).items()]
                print('|-+', f'<{individual}>', *data)
        print(' ')


def print_latlon(spart):
    data = [
        (individual, lat, lon)
        for individual in spart.getIndividuals()
        for (lat, lon) in (spart.getIndividualLatLon(individual),)
    ]
    df = pd.DataFrame(data, columns=['id', 'lat', 'lon'])
    df = df.set_index('id')

    df.to_csv(stdout, sep='\t')


if __name__ == '__main__':
    input = argv[1]
    spart = Spart.fromXML(input)
    print()
    print_tree(spart)
    print()
    print_latlon(spart)
    print()
