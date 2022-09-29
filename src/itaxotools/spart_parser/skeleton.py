
from typing import Dict, Set, List
from dataclasses import dataclass

from . import SpartParser


# probably ignore this
@dataclass
class Individual():
    name: str
    score: int = None


# def ...
#     return Individual('this thing', 12)


class SpartDict(dict):

    @property
    def individuals(self) -> Set[Individual]:
        ...

    def partitions(self) -> List:
        ...

    def add_individual(self, individual: Individual):
        ...

    def add_spartition(self, name, subsets):
        self['spartitions'] = ...

    def write_xml(self, path):
        with open(path, 'w') as file:
            file.write('')

    def write_regular(self, path):
        ...

    @classmethod
    def read_xml(cls, path):
        spartParser = SpartParser(str(path))
        return spartParser.generateData()



...

#
# spart = SpartDict()
#
# for individual in individuals:
#     spart.add_individual(individual)
#
# for spartition in spartitions:
#     spart.add_spartition(spartition.name, [{'a'}, {'b', 'c'}, {'d'}] )

...
