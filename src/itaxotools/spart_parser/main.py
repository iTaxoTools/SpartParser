import collections
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re,os
from datetime import datetime
from sys import argv
from pathlib import Path

class Spart:

    def __init__(self):
        self.spartDict = {}

    def individuals(self, individualName, **kwargs):
        self.spartDict['individuals'] = {}
        self.spartDict['individuals'][individualName] = {}
        for key, val in kwargs.items():
            self.spartDict['individuals'][individualName][key] = val
        return self.spartDict

    def toXML(self, spartDict):
        root = ET.Element("root")
        project_name = ET.SubElement(root, 'project_name').text = spartDict['project_name']
        date = ET.SubElement(root, 'date').text = spartDict['date']

        #individuals
        individuals = ET.SubElement(root, "individuals")
        for individual, data in spartDict['individuals'].items():
            ET.SubElement(individuals, "individual", id=individual, attrib=data)

        #spartitions
        spartitions = ET.SubElement(root, "spartitions")
        spartitionTags = {}
        for spartition, data in spartDict['spartitions'].items():
            for tag, val in data.items():
                if str(tag).isnumeric() or tag == 'concordances':
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
            for subsetNum, val in data.items():
                if str(subsetNum).isnumeric():
                    for key, val in data[subsetNum].items():
                        if key != 'individuals':
                            subsetTags[key] = val
            subsetET = ET.SubElement(subsetsET, "subset", attrib=subsetTags)
            #Subsets/subset/individual
            for subsetNum, val in data.items():
                if str(subsetNum).isnumeric():
                    for key, val in data[subsetNum].items():
                        if key == 'individuals':
                            for indi, v in data[subsetNum][key].items():
                                subIndividualTags['ref'] = indi
                                if data[subsetNum][key][indi]:
                                    for k, v in data[subsetNum][key][indi].items():
                                        subIndividualTags[k] = v
                                subindividualET = ET.SubElement(subsetET, "individual", attrib=subIndividualTags)

        #latlon

        tree = ET.ElementTree(root)
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        time.sleep(0.00001)
        fileName = 'SPART_TEST' + datetime.utcnow().strftime("%Y%m%d%H%M%S%f") + ".xml"
        with open(fileName, "w") as f:
            f.write(xmlstr)

    def toRegularSpart(self, spartDict):
        time.sleep(0.00001)
        fileName = 'LIMES_TEST' + datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        with open(fileName + '.spart', 'w+') as f:
            f.write('begin spart;')
            numSpartitions = len(spartDict['spartitions'])
            subCountDict = {}
            for key, val in spartDict.items():
                if key == 'project_name' or key == 'date':
                    f.write(f'\n\n{key} = {val};')
                if key == 'spartitions':
                    n_spartition = f'{numSpartitions} : '
                    n_individuals = ''
                    n_subsets = ''
                    n_subsets_scores = ''
                    for spNum in range(1, numSpartitions+1):
                        if checkKey(spartDict['spartitions'][n2w(spNum) + ' spartition'], 'Label'):
                            n_spartition += spartDict['spartitions'][n2w(spNum) + ' spartition']['Label'] +' /'
                        #count subsets
                        indiCount = 0
                        for subNum, val in spartDict['spartitions'][n2w(spNum) + ' spartition'].items():
                            if str(subNum).isnumeric():
                                subCountDict[spNum] = 1 + subCountDict.get(spNum, 0)
                                if checkKey(spartDict['spartitions'][n2w(spNum) + ' spartition'][subNum], 'score'):
                                    n_subsets_scores += f"{spartDict['spartitions'][n2w(spNum) + ' spartition'][subNum]['score'] + ','}"
                                for _ in spartDict['spartitions'][n2w(spNum) + ' spartition'][subNum]['individuals'].keys():
                                    indiCount += 1

                        n_individuals += str(indiCount) + ' /'
                    for subCount in range(1, len(subCountDict) + 1):
                        n_subsets += str(subCountDict[subCount]) + ' /'

                    f.write(f'\n\nn_spartition = {n_spartition[:-2]};')
                    f.write(f'\n\nn_individuals = {n_individuals[:-2]};')
                    if n_subsets_scores:
                        f.write(f'\n\nn_subsets = {n_subsets[:-2]}:{n_subsets_scores[:-2]};')
                    else:
                        f.write(f'\n\nn_subsets = {n_subsets[:-2]};')
                    f.write(f'\n\nindividual_assignment = ')

                    for indiName in spartDict["individuals"].keys():
                        inSub = ''
                        for spNum in range(1, numSpartitions +1):
                            for sub in range(1, subCountDict[spNum] + 1):
                                if checkKey(spartDict['spartitions'][n2w(spNum) + ' spartition'], sub):
                                    if indiName in spartDict['spartitions'][n2w(spNum) + ' spartition'][sub]['individuals']:
                                        inSub += str(sub) + ' /'
                        f.write(f'\n{indiName} : {inSub[:-2]} ')
                    f.write(';')


            f.write('\nend;')
            f.close()

    def spartitions(self):
        pass


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
            spartition[remark.text]['concordances']= {}
            spartition[remark.text]['concordances']['concordance'] = {}

            for index, val in remarks.attrib.items():
                spartition[remark.text][index] = val

            for subsets in remarks.findall('subsets/subset'):
                label = subsets.attrib['label']
                spartition[remark.text][label] = {}
                spartition[remark.text][label]['individuals'] = {}
                #Subset
                for index, val in subsets.attrib.items():
                    if index == 'label':
                        continue
                    spartition[remark.text][label][index] = val

                #Subset individuals
                for individuals in subsets.findall('individual'):
                    individual_id = individuals.attrib['ref']
                    spartition[remark.text][label]['individuals'][individual_id]= {}
                    for index, val in individuals.attrib.items():
                        if index == 'ref':
                            continue
                        spartition[remark.text][label]['individuals'][individual_id][index] = val

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
                print(indi)
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
                print(result.group(1))
                getSubsets = result.group(1).split("=")[1].strip()
                subset = getSubsets.split(":")
                spartList =  subset[1].strip().split('/')
                if spartList[-1][-1] == ';':
                    spartList[-1] = spartList[-1][:-1]
                numOfspart = int(subset[0])

        for spartion in range(1,numOfspart+1):
            spartionNumber = n2w(spartion) + ' spartition'
            self.spartDict['spartitions'][spartionNumber] = {'Label' : spartList[spartion-1].strip()}
            count = 0
            #create subsets
            if subsetCounttList[-1][0][-1] == ';':
                subsetCounttList[-1][0] = subsetCounttList[-1][0][:-1]
            print(subsetCounttList)
            for subset in range(int(subsetCounttList[spartion-1][0].strip())):
                count += 1
                self.spartDict['spartitions'][spartionNumber][count] = {}

            count = 0
            #add subset score
            for subset in range(int(subsetCounttList[spartion-1][0].strip())):
                count += 1
                if subsetCounttList[spartion-1][1] != '':
                    scoreList = subsetCounttList[spartion - 1][1].split(',')
                    self.spartDict['spartitions'][spartionNumber][count] = {'score': scoreList[count-1]}
                self.spartDict['spartitions'][spartionNumber][count]['individuals'] = {}


        for subsets in self.individualAssignments.keys():
            subsetList = self.individualAssignments[subsets].split('/')
            count = 0
            for subset in range(1,numOfspart+1):
                spartionNumber = n2w(subset) + ' spartition'
                self.spartDict['spartitions'][spartionNumber][int(subsetList[count].strip())]['individuals'][subsets] = {}
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


def main(file):
    #file = argv[1]

    path = Path(file)
    if path.suffix == '.xml':
        spartParser = SpartParser(str(path))
    else:
        spartParser = SpartParserRegular(str(path))
    x = spartParser.generateData()
    # from json import dumps
    # return dumps(x)
    return x



if __name__ == '__main__':
    # print(main())
    s = Spart()
    # xml_str = s.toXML(main())
    # root = etree.fromstring(xml_str)
    # print(etree.tostring(root, pretty_print=True).decode())
    exmDir = os.listdir("..\..\..\examples")
    for f in exmDir:
        path = Path(f)
        sp = main('..\..\..\examples\\' + f)
        s.toXML(sp)
        s.toRegularSpart(sp)