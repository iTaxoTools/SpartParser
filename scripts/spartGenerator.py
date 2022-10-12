from sys import argv
from time import time
from pathlib import Path
from random import random
from datetime import datetime

from itaxotools.spart_parser import Spart

#Num of individual in subset should all be the same

numIndividuals = int(argv[1])
numSpartitions = int(argv[2])
numSubsetsInSpartition = int(argv[3])
numIndividualsInSubset = int(argv[4])
file = Path(argv[5])

extension = file.suffix


time_start = time()


spart = Spart()
spart.project_name = 'custom_generated_file'
spart.date = datetime(2022, 10, 2, 12, 0, 0)

#Add individual
for indi in range(1, numIndividuals+1):
    spart.addIndividual(f'individual_{indi}')

count = 1
spScore = 1.0
#Add spartition
for spartition in range(1, numSpartitions + 1):
    spart.addSpartition(f'spartition_{spartition}',
                        spartitionScore=spScore,
                        individual_score_type=f'individual_score_{spartition}',
                        spartition_score_type=f'spartition_score_{spartition}',
                        subset_score_type=f'subset_score_{spartition}')
    spScore += 1
    for subset in range(1, numSubsetsInSpartition + 1):
        spart.addSubset(f'spartition_{spartition}', f'{subset}')
        for _ in range(1, numIndividualsInSubset + 1):
            spart.addSubsetIndividual(f'spartition_{spartition}', f'{subset}', f'individual_{count}', score=random())
            count += 1
    count = 1

time_create = time()
print(f'Created Spart instance in {time_create-time_start: .4f} seconds.')

if extension.lower() == '.xml':
    spart.toXML(file)
elif extension.lower() == '.spart':
    spart.toMatricial(file)

time_write = time()
print(f'Exported Spart to file in {time_write-time_create: .4f} seconds.')
