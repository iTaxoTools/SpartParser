import collections, time, re, os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from sys import argv
from pathlib import Path

class CannotParseFile(Exception):
    def __init__(self, path: Path):
        self.path = path
        super().__init__((f'Cannot parse file: {str(path)}'))

class Spart:

    def __init__(self, spartDict: dict = None):
        if spartDict is None:
            self.spartDict = {}
            self.spartDict['project_name'] = {}
            self.spartDict['date'] = {}
            self.spartDict['individuals'] = {}
            self.spartDict['spartitions'] = {}
        else:
            self.spartDict = spartDict

    @classmethod
    def fromMatricial(cls, path: Path):
        """Parse a matricial spart file and return a Spart instance"""
        parser = SpartParserRegular(str(path))
        spartDict = parser.generateData()
        return cls(spartDict)

    @classmethod
    def fromXML(cls, path: Path):
        """Parse an XML spart file and return a Spart instance"""
        parser = SpartParser(str(path))
        spartDict = parser.generateData()
        return cls(spartDict)

    @classmethod
    def fromPath(cls, path: Path):
        """Parse any supported file and return a Spart instance"""
        try:
            if path.suffix == '.xml':
                return cls.fromXML(path)
            else:
                return cls.fromMatricial(path)
        except:
            raise CannotParseFile(path)

    def toXML(self, path: Path):
        root = ET.Element("root")
        project_name = ET.SubElement(root, 'project_name').text = self.spartDict['project_name']
        date = ET.SubElement(root, 'date').text = self.spartDict['date']

        #individuals
        individuals = ET.SubElement(root, "individuals")
        for individual, data in self.spartDict['individuals'].items():
            ET.SubElement(individuals, "individual", id=individual, attrib=data)

        #spartitions
        spartitions = ET.SubElement(root, "spartitions")
        spartitionTags = {}
        for spartition, data in self.spartDict['spartitions'].items():
            for tag, val in data.items():
                if tag == 'subsets' or tag == 'concordances':
                    continue
                else:
                    spartitionTags[tag] = val
            spartitionET = ET.SubElement(spartitions, "spartition", attrib=spartitionTags)
            remark = ET.SubElement(spartitionET, "remarks")
            remark.text = spartition
            subsetsET = ET.SubElement(remark, "subsets")
            subsetTags = {}
            subIndividualTags = {}
            #Subsets/subset
            for subsetNum, val in data['subsets'].items():
                subsetTags['label'] = subsetNum
                for key, val in data['subsets'][subsetNum].items():
                    if key != 'individuals':
                        subsetTags[key] = val
                subsetET = ET.SubElement(subsetsET, "subset", attrib=subsetTags)
                #Subsets/subset/individual
                for key, val in data['subsets'][subsetNum].items():
                    if key == 'individuals':
                        for indi, v in data['subsets'][subsetNum][key].items():
                            subIndividualTags['ref'] = indi
                            if data['subsets'][subsetNum][key][indi]:
                                for k, v in data['subsets'][subsetNum][key][indi].items():
                                    subIndividualTags[k] = v
                            subindividualET = ET.SubElement(subsetET, "individual", attrib=subIndividualTags)

        #latlon

        tree = ET.ElementTree(root)
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        with open(path, "w") as f:
            f.write(xmlstr)

    def toMatricial(self, path: Path):
        with open(path, 'w+') as f:
            f.write('begin spart;')
            numSpartitions = len(self.spartDict['spartitions'])
            subCountDict = {}
            if checkKey(self.spartDict, 'project_name'):
                f.write(f'\n\nproject_name = {self.spartDict["project_name"]};')
            if checkKey(self.spartDict, 'date'):
                f.write(f'\n\ndate = {self.spartDict["date"]};')
            for key, val in self.spartDict.items():
                if key == 'spartitions':
                    n_spartition = f'{numSpartitions} : '
                    n_individuals = ''
                    n_subsets = ''
                    n_subsets_scores = ''
                    n_subsets_strings = []
                    for spNum in range(1, numSpartitions+1):
                        if checkKey(self.spartDict['spartitions'][n2w(spNum) + ' spartition'], 'label'):
                            n_spartition += self.spartDict['spartitions'][n2w(spNum) + ' spartition']['label'] +' / '
                        #count subsets
                        indiCount = 0
                        for subNum, val in self.spartDict['spartitions'][n2w(spNum) + ' spartition']['subsets'].items():
                            if subNum.isnumeric():
                                subCountDict[spNum] = 1 + subCountDict.get(spNum, 0)
                                if checkKey(self.spartDict['spartitions'][n2w(spNum) + ' spartition']['subsets'][subNum], 'score'):
                                    n_subsets_scores += f"{self.spartDict['spartitions'][n2w(spNum) + ' spartition']['subsets'][subNum]['score'] + ','}"
                                for _ in self.spartDict['spartitions'][n2w(spNum) + ' spartition']['subsets'][subNum]['individuals'].keys():
                                    indiCount += 1
                        n_subsets_strings.append(f"{str(subCountDict[spNum])}:{n_subsets_scores}")
                        n_subsets_scores = ""
                        n_individuals += str(indiCount) + ' / '
                    for subCount in range(1, len(subCountDict) + 1):
                        n_subsets += n_subsets_strings[subCount-1][:-1]+ ' / '

                    f.write(f'\n\nn_spartition = {n_spartition[:-3]};')
                    f.write(f'\n\nn_individuals = {n_individuals[:-3]};')
                    if n_subsets_scores:
                        f.write(f'\n\nn_subsets = {n_subsets[:-3]}:{n_subsets_scores[:-1]};')
                    else:
                        f.write(f'\n\nn_subsets = {n_subsets[:-3]};')
                    f.write(f'\n\nindividual_assignment = ')

                    for indiName in self.spartDict["individuals"].keys():
                        inSub = ''
                        for spNum in range(1, numSpartitions +1):
                            for sub in range(1, subCountDict[spNum] + 1):
                                if checkKey(self.spartDict['spartitions'][n2w(spNum) + ' spartition']['subsets'], str(sub)):
                                    if indiName in self.spartDict['spartitions'][n2w(spNum) + ' spartition']['subsets'][str(sub)]['individuals']:
                                        inSub += str(sub) + ' / '
                        f.write(f'\n{indiName} : {inSub[:-3]} ')
                    f.write(';')


            f.write('\nend;')
            f.close()

    def addIndividual(self, individualName, **kwargs):
        self.spartDict['individuals'][individualName] = {}
        for key, val in kwargs.items():
            self.spartDict['individuals'][individualName][key] = val
        return self.spartDict

    def addSpartition(self, label: str, **kwargs):
        sparitionNumber = len(self.spartDict['spartitions']) + 1
        self.spartDict['spartitions'][n2w(sparitionNumber) + ' sparition'] = {}
        self.spartDict['spartitions'][n2w(sparitionNumber) + ' sparition']['label'] = label

    def addSpartitionSubsets(self, label: str, numSubset: int, **kwargs):
        for spartition in self.spartDict['spartitions'].keys():
            self.spartDict['spartitions'][spartition]['subsets'] = {}
            for tag in self.spartDict['spartitions'][spartition].keys():
                if tag == 'label':
                    if self.spartDict['spartitions'][spartition][tag] == label:
                        for subNum in range(1, numSubset+ 1):
                            self.spartDict['spartitions'][spartition]['subsets'][str(subNum)] = {}
                            for key, val in kwargs.items():
                                self.spartDict['spartitions'][spartition]['subsets'][key] = val

    def addSubsetIndividuals(self, spartitionLabel: str, subsetNum: str, **kwargs):
        for spartition in self.spartDict['spartitions'].keys():
            for tag in self.spartDict['spartitions'][spartition].keys():
                if tag == 'label':
                    self.spartDict['spartitions'][spartition]['subsets'][subsetNum]['individuals'] = {}
                    if self.spartDict['spartitions'][spartition][tag] == spartitionLabel:
                        for key, val in kwargs.items():
                            self.spartDict['spartitions'][spartition]['subsets'][subsetNum]['individuals'][key] = val

    def getIndividuals(self) -> list[str]:
        """Returns a list with the ids of each individual"""
        individuals_list = []
        for individual in self.spartDict['individuals'].keys():
            individuals_list.append(individual)

        return individuals_list

    def getIndividualData(self, id: str) -> dict[str, object]:
        """Returns extra information about the given individual id"""
        if checkKey(self.spartDict['individuals'], id):
            return self.spartDict['individuals'][id]

    def getSpartitions(self) -> list[str]:
        """Returns a list with the labels of each spartition"""
        labels_list = []
        for spartition in self.spartDict['spartitions'].keys():
            for tag in self.spartDict['spartitions'][spartition].keys():
                if tag == 'label':
                    labels_list.append(self.spartDict['spartitions'][spartition][tag])
        return labels_list

    def getSpartitionData(self, label: str) -> dict[str, object]:
        """Returns extra information about the given spartition"""

        for spartition in self.spartDict['spartitions'].keys():
            for tag in self.spartDict['spartitions'][spartition].keys():
                if self.spartDict['spartitions'][spartition]['label'] == label:
                    return self.spartDict['spartitions'][spartition]

    def getSpartitionSubsets(self, label: str) -> list[str]:
        """Returns a list with the labels of all subsets of the given spartition"""
        subsetLabel_list = []
        for spartition in self.spartDict['spartitions'].keys():
            for tag in self.spartDict['spartitions'][spartition].keys():
                if tag == 'label':
                    if self.spartDict['spartitions'][spartition][tag] == label:
                        for subLabel in self.spartDict['spartitions'][spartition]['subsets'].keys():
                            subsetLabel_list.append(subLabel)
        return subsetLabel_list

    def getSubsetIndividuals(self, spartitionLabel: str, subsetNum: str) -> list[str]:
        """Returns a list of all individuals contained in the spartition
        and subset specified by the given labels."""
        individuals_list = []
        for spartition in self.spartDict['spartitions'].keys():
            for tag in self.spartDict['spartitions'][spartition].keys():
                if tag == 'label':
                    if self.spartDict['spartitions'][spartition][tag] == spartitionLabel:
                        for key, val in self.spartDict['spartitions'][spartition]['subsets'][subsetNum].items():
                            if key =='individuals':
                                for individual in self.spartDict['spartitions'][spartition]['subsets'][subsetNum]['individuals'].keys():
                                    individuals_list.append(individual)
        return individuals_list

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
            spartition[remark.text]['concordances']['concordance'] = {}

            for index, val in remarks.attrib.items():
                spartition[remark.text][index] = val

            for subsets in remarks.findall('subsets/subset'):
                label = subsets.attrib['label']
                spartition[remark.text]['subsets'][label] = {}
                spartition[remark.text]['subsets'][label]['individuals'] = {}
                #Subset
                for index, val in subsets.attrib.items():
                    if index == 'label':
                        continue
                    spartition[remark.text]['subsets'][label][index] = val

                #Subset individuals
                for individuals in subsets.findall('individual'):
                    individual_id = individuals.attrib['ref']
                    spartition[remark.text]['subsets'][label]['individuals'][individual_id]= {}
                    for index, val in individuals.attrib.items():
                        if index == 'ref':
                            continue
                        spartition[remark.text]['subsets'][label]['individuals'][individual_id][index] = val

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
        return spartition

    def generateData(self):
        self.getProjectinfo()
        self.getindividuals()
        self.getSpartitions()
        self.getLatLon()
        self.getSequences()
        return self.spartDict

class SpartParserRegular:

    def __init__(self, fileName):
        self.fileName = fileName
        self.spartDict = {}
        with open(fileName, 'r+') as f:
            self.spartFile = f.readlines()
        self.keysDict = {}
        self.individualAssignments = {}

    def getKeys(self):
        for line in self.spartFile:
            n = line.split('=')
            if len(n)> 1:
                self.keysDict[n[0].strip().lower()] = n[0].strip()

    def getProjectinfo(self):
        for line in self.spartFile:
            prjectName = re.search(self.keysDict['project_name'] + '\s?=\s?([^;]+);' , line)
            if prjectName:
                self.spartDict["project_name"] = prjectName.group(1)
            date = re.search(self.keysDict['date'] + '\s?=\s?([^;]+);' , line)
            if date:
                self.spartDict["date"] = date.group(1)

    def getindividuals(self):
        self.spartDict['individuals'] = {}
        #individuals
        startIndi = False
        count = 0
        for line in self.spartFile:
            result = re.search(f'({self.keysDict["individual_assignment"]})', line)
            if result:
                startIndi = True
                continue
            if startIndi and line.strip() == ';':
                startIndi = False
                break
            if startIndi and line.strip()[-1] == ';':
                indi = line.strip().split(':')
                self.spartDict['individuals'][indi[0].strip()] = {}
                self.individualAssignments[indi[0].strip()] = indi[1][:-1].strip()
                break
            elif startIndi:
                indi = line.strip().split(':')
                self.spartDict['individuals'][indi[0].strip()] = {}
                self.individualAssignments[indi[0].strip()] = indi[1].strip()

        return self.spartDict

    def getSpartitions(self):
        self.spartDict['spartitions'] = {}
        spartList = []
        subsetCounttList = []
        numOfspart = '0'
        for line in self.spartFile:
            #subsets
            result = re.search(f'({self.keysDict["n_subsets"]}.*)', line)
            if result:
                getSubsets = result.group(1).split("=")[1].strip()
                counttList =  getSubsets.strip().split('/')
                for scores in counttList:
                    score = scores.strip().split(':')
                    subsetCounttList.append([score[0],score[1] if score[-1] != score[0]  else ''])
            #spartitions
            result = re.search(f'({self.keysDict["n_spartitions"]}.*)', line)
            if result:
                getSubsets = result.group(1).split("=")[1].strip()
                subset = getSubsets.split(":")
                spartList =  subset[1].strip().split('/')
                if spartList[-1][-1] == ';':
                    spartList[-1] = spartList[-1][:-1]
                numOfspart = int(subset[0])

        for spartion in range(1,numOfspart+1):
            spartionNumber = n2w(spartion) + ' spartition'
            self.spartDict['spartitions'][spartionNumber] = {'label' : spartList[spartion-1].strip()}
            self.spartDict['spartitions'][spartionNumber]['subsets'] = {}
            count = 0
            #create subsets
            if subsetCounttList[-1][0][-1] == ';':
                subsetCounttList[-1][0] = subsetCounttList[-1][0][:-1]
            for subset in range(int(subsetCounttList[spartion-1][0].strip())):
                count += 1
                self.spartDict['spartitions'][spartionNumber]['subsets'][str(count)] = {}

            count = 0
            #add subset score
            for subset in range(int(subsetCounttList[spartion-1][0].strip())):
                count += 1
                if subsetCounttList[spartion-1][1] != '':
                    scoreList = subsetCounttList[spartion - 1][1].split(',')
                    if scoreList[-1][-1] == ';':
                        scoreList[-1] = scoreList[-1][:-1]
                    self.spartDict['spartitions'][spartionNumber]['subsets'][str(count)] = {'score': scoreList[count-1]}
                self.spartDict['spartitions'][spartionNumber]['subsets'][str(count)]['individuals'] = {}


        for subsets in self.individualAssignments.keys():
            subsetList = self.individualAssignments[subsets].split('/')
            count = 0
            for subset in range(1,numOfspart+1):
                spartionNumber = n2w(subset) + ' spartition'
                self.spartDict['spartitions'][spartionNumber]['subsets'][str(subsetList[count].strip())]['individuals'][subsets] = {}
                count +=1
        return self.spartDict

    def generateData(self):
        self.getKeys()
        self.getProjectinfo()
        self.getindividuals()
        self.getSpartitions()
        return self.spartDict

def n2w(n):
    num2words = {1: 'First', 2: 'Second', 3: 'Third', 4: 'Fourth', 5: 'Fifth', 6: 'Sixth', 7: 'Seventh', 8: 'Eight',
                 9: 'Ninth', 10: 'Tenth', 11: 'Eleventh', 12: 'Twelfth', 13: 'Thirteenth', 14: 'Fourteenth',
                 15: 'Fifteenth', 16: 'Sixteenth', 17: 'Seventeenth', 18: 'Eighteenth', 19: 'Nineteenth',
                 20: 'Twentieth|Twenty', 30: 'Thirtieth|Thirty', 40: 'Fortieth|Forty', 50: 'Fiftieth|Fifty',
                 60: 'Sixtieth|Sixty', 70: 'Seventieth|Seventy', 80: 'Eightieth|Eighty', 90: 'Ninetieth|Ninety',
                 0: 'Zero'}
    try:
        num2word = num2words[n].split('|')[0]
        return num2word
    except KeyError:
        try:
            num2word = num2words[n - n % 10].split('|')[1]
            return num2word +'-'+num2words[n % 10].lower()
        except KeyError:
            raise

def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}

def checkKey(dic, key):
    if key in dic.keys():
        return True
    else:
        return False

def main():
    path = Path(argv[1])
    spart = Spart.fromPath(path)
    from json import dumps
    print(dumps(spart.spartDict))


def demo():
    demoDir = Path("demo")
    demoDir.mkdir(exist_ok=True)

    exmDir = Path("..\..\..\examples")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    for src in exmDir.iterdir():
        spart = Spart.fromPath(src)
        dest_xml = demoDir / f'{src.name}.{timestamp}.xml'
        spart.toXML(dest_xml)
        dest_mat = demoDir / f'{src.name}.{timestamp}.spart'
        spart.toMatricial(dest_mat)

if __name__ == '__main__':
    demo()