import xml.etree.ElementTree as ET

class SpartParser:

    def __init__(self, spartFile):
        self.spartFile = spartFile
        self.spartDict = {}
        self.tree = ET.parse(self.spartFile)
        self.root = self.tree.getroot()

    def getProjectinfo(self):
        self.spartDict["project_name"] = self.root.find("project_name").text
        self.spartDict["date"] = self.root.find("date").text

    def getindividuals(self):
        individuals = {}
        for individual in self.root.findall('individuals/individual'):
            id = individual.attrib['id']
            individuals[id] = without_keys(individual.attrib, "id")
        self.spartDict['individuals'] = individuals

    def getSequences(self):
        sequences = {}
        for individual in self.root.findall('sequences/sequence'):
            id = individual.find('notes').attrib['individual']
            bank_accession = individual.find('genbank_accession')
            markercode = individual.find('markercode')
            nucleotides = individual.find('nucleotides')
            sequences[id] = {}
            sequences[id]['genbank_accession'] = bank_accession.text
            sequences[id]['markercode'] = markercode.text
            sequences[id]['nucleotides'] = nucleotides.text
        self.spartDict['sequences'] = sequences

    def getLatLon(self):
        latlon = {}
        for individual in self.root.findall('latlon/coordinates'):
            id = individual.attrib['locality']
            latlon[id] = without_keys(individual.attrib, "locality")
        self.spartDict['latlon'] = latlon

    def getSpartitions(self):
        spartition = {}

        for remarks in self.root.findall('spartitions/spartition'):
            remark = remarks.find('remarks')
            spartition[remark.text] = {}
            spartition[remark.text]['subsets'] = {}
            spartition[remark.text]['concordances']= {}
            spartition[remark.text]['subsets']['subset'] = {}
            spartition[remark.text]['concordances']['concordance'] = {}

            for index, val in remarks.attrib.items():
                spartition[remark.text][index] = val

            for subsets in remarks.findall('subsets/subset'):
                label = subsets.attrib['label']
                spartition[remark.text]['subsets']['subset'][label] = {}
                spartition[remark.text]['subsets']['subset'][label]['individuals'] = {}
                #Subset
                for index, val in subsets.attrib.items():
                    if index == 'label':
                        continue
                    spartition[remark.text]['subsets']['subset'][label][index] = val

                #Subset individuals
                for individuals in subsets.findall('individual'):
                    individual_id = individuals.attrib['ref']
                    spartition[remark.text]['subsets']['subset'][label]['individuals'][individual_id]= {}
                    for index, val in individuals.attrib.items():
                        if index == 'ref':
                            continue
                        spartition[remark.text]['subsets']['subset'][label]['individuals'][individual_id][index] = val

            for concordances in remarks.findall('concordances/concordance'):
                label = concordances.attrib['label']
                spartition[remark.text]['concordances']['concordance'][label] = {}
                date = concordances.find('date')
                concordantsubsets = concordances.findall('concordantsubsets')
                spartition[remark.text]['concordances']['concordance'][label]['date'] = date.text
                spartition[remark.text]['concordances']['concordance'][label]['concordantsubsets'] = []
                for index, val in concordances.attrib.items():
                    if index == 'label':
                        continue
                    spartition[remark.text]['concordances']['concordance'][label][index] = val

                for subset in concordantsubsets:
                    spartition[remark.text]['concordances']['concordance'][label]['concordantsubsets'].append(subset.attrib['subsetnumber'])

        self.spartDict['spartitions'] = spartition

    def generateData(self):
        self.getProjectinfo()
        self.getindividuals()
        self.getSpartitions()
        self.getLatLon()
        self.getSequences()
        return self.spartDict

def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}

if __name__ == '__main__':
    spartParser = SpartParser('spart.xml')
    print(spartParser.generateData())