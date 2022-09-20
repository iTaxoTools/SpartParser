
from . import SpartParser

class SpartDict(dict):

    def add_individual(self, name):
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
