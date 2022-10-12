from sys import argv
from itaxotools.spart_parser import Spart
import random
import datetime
from pathlib import Path
#numIndi numSpartition numSubsets fileExtenstion
spart = Spart()
spart.project_name = 'custom_generated_file'
spart.date = datetime.datetime(2022, 10, 2, 12, 0, 0)
numIndividuals = argv[1]
numSpartitions = argv[2]
numSubsetsInSpartition = argv[3]
file = Path(argv[4])
extension = file.suffix


#Num of individual in subset should all be the same

#Add individual
for indi in range(1, int(numIndividuals)+1):
    spart.addIndividual(f'individual_{indi}')
    
count = 1
spScore = 1.0
#Add spartition
for spartition in range(1, int(numSpartitions) + 1):
    spart.addSpartition(f'spartition_{spartition}',
                        spartitionScore=spScore,
                        individual_score_type=f'individual_score_{spartition}',
                        spartition_score_type=f'spartition_score_{spartition}',
                        subset_score_type=f'subset_score_{spartition}')
    spScore += 1
    individualSet = set()
    for subset in range(1, int(numSubsetsInSpartition) + 1):
        spart.addSubset(f'spartition_{spartition}', f'{subset}')
        for _ in range(1, int(numSubsetsInSpartition) + 1):
            spart.addSubsetIndividual(f'spartition_{spartition}', f'{subset}', f'individual_{count}')
            count += 1
    count = 1

if extension.lower() == '.xml':
    spart.toXML(file)
elif extension.lower() == '.spart':
    spart.toMatricial(file)


print(numIndividuals, numSpartitions, numSubsetsInSpartition, file)

