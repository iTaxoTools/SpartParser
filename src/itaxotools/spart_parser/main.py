from __future__ import annotations
import collections, time, re, os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from sys import argv
from pathlib import Path


class Spart:
    """Holds a list of individuals, spartitions and their subsets"""

    def __init__(self, spartDict: dict = None):
        """Create a new empty dataset by default"""
        if spartDict is None:
            self.spartDict = {}
            self.spartDict['project_name'] = ''
            self.spartDict['date'] = ''
            self.spartDict['individuals'] = {}
            self.spartDict['spartitions'] = {}
        else:
            self.spartDict = spartDict

    @classmethod
    def fromMatricial(cls, path: Path) -> Spart:
        """Parse a matricial spart file and return a Spart instance"""
        parser = SpartParserRegular(str(path))
        spartDict = parser.generateData()
        return cls(spartDict)

    @classmethod
    def fromXML(cls, path: Path) -> Spart:
        """Parse an XML spart file and return a Spart instance"""
        parser = SpartParser(str(path))
        spartDict = parser.generateData()
        return cls(spartDict)

    @classmethod
    def fromXML_dev(cls, path: Path) -> Spart:
        """Parse an XML spart file and return a Spart instance"""
        parser = SpartParserXML(str(path))
        spartDict = parser.generateData()
        return cls(spartDict)

    @classmethod
    def fromPath(cls, path: Path) -> Spart:
        """Parse any supported file and return a Spart instance"""
        if is_path_xml(path):
            return cls.fromXML(path)
        else:
            return cls.fromMatricial(path)

    def toXML(self, path: Path) -> None:
        """Convert Spart instance to XML file"""
        root = ET.Element("root")
        project_name = ET.SubElement(root, 'project_name').text = self.spartDict['project_name']
        date = ET.SubElement(root, 'date').text = self.spartDict['date']

        #Write Individuals to xml
        individuals = ET.SubElement(root, "individuals")
        for individual, data in self.spartDict['individuals'].items():
            ET.SubElement(individuals, "individual", id=individual, attrib=data)

        #Write Spartitions to xml
        spartitions = ET.SubElement(root, "spartitions")
        spartitionTags = {}
        spartitionsKeys = {'spartition_score': 'spartitionScore', 'spartition_score_type': 'spartitionScoreType',
                           'individual_score_type': 'individualScoreType', 'subset_score_type': 'subsetScoreType'}
        for spartition, data in self.spartDict['spartitions'].items():
            for tag, val in data.items():
                if tag == 'subsets' or tag == 'concordances':
                    continue
                else:
                    if tag in spartitionsKeys:
                        tag = spartitionsKeys[tag]
                    if val:
                        spartitionTags[tag] = str(val)

            spartitionET = ET.SubElement(spartitions, "spartition", attrib=spartitionTags)
            spartitionTags = {}
            remark = ET.SubElement(spartitionET, "remarks")
            if not checkKey(self.spartDict['spartitions'][spartition], 'remarks'):
                remark.text = n2w(int(spartition)) + ' spartition'
            else:
                remark.text = self.spartDict['spartitions'][spartition]['remarks']
            subsetsET = ET.SubElement(spartitionET, "subsets")
            subsetTags = {}
            subIndividualTags = {}
            #Subsets/subset
            for subsetNum, val in data['subsets'].items():
                subsetTags['label'] = subsetNum
                for key, val in data['subsets'][subsetNum].items():
                    if key != 'individuals':
                        if val:
                            subsetTags[key] = str(val)

                subsetET = ET.SubElement(subsetsET, "subset", attrib=subsetTags)
                subsetTags = {}
                #Subsets/subset/individual
                if subsetNum.isnumeric():
                    for indi, val in data['subsets'][subsetNum]['individuals'].items():
                        subIndividualTags['ref'] = indi
                        if data['subsets'][subsetNum]['individuals'][indi]:
                            for k, v in data['subsets'][subsetNum]['individuals'][indi].items():
                                if v:
                                    subIndividualTags[k] = str(v)

                        subindividualET = ET.SubElement(subsetET, "individual", attrib=subIndividualTags)
                        subsetTags = {}

        #Write latlon  to xml

        #Write Sequences to xml

        #Create XML file
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        with open(path, "w") as f:
            f.write(xmlstr)

    def toMatricial(self, path: Path) -> None:
        """Convert Spart instance to matricial spart file"""

        #Creating spart file with given path
        with open(path, 'w') as f:

            f.write('begin spart;')
            numSpartitions = len(self.spartDict['spartitions'])
            subCountDict = {}
            if checkKey(self.spartDict, 'project_name'):
                f.write(f'\n\nproject_name = {self.spartDict["project_name"]};')
            if checkKey(self.spartDict, 'date'):
                f.write(f'\n\ndate = {self.spartDict["date"]};')

            n_spartition = f'{numSpartitions} : '
            n_individuals = ''
            n_subsets = ''
            n_subsets_scores = ''
            subset_score_type = ''
            spartition_score_type = ''
            individual_score_type = ''
            hasSubset_score_type = False
            hasSpartition_score_type = False
            hasIndividual_score_type = False
            n_subsets_strings = []

            for spNum in range(1, numSpartitions+1):
                #label
                if checkKey(self.spartDict['spartitions'][str(spNum)], 'label'):
                    #spartition_score
                    if checkKey(self.spartDict['spartitions'][str(spNum)], 'spartition_score'):
                        n_spartition += self.spartDict['spartitions'][str(spNum)]['label'] + ', '
                        if not self.spartDict['spartitions'][str(spNum)]['spartition_score'] is None:
                            n_spartition += f"{str(self.spartDict['spartitions'][str(spNum)]['spartition_score'])}  / "
                        else:
                            n_spartition += "? / "
                    else:
                        n_spartition += self.spartDict['spartitions'][str(spNum)]['label'] + ' / '
                #subset_score_type

                if checkKey(self.spartDict['spartitions'][str(spNum)], 'subset_score_type'):
                    hasSubset_score_type = True
                    if self.spartDict['spartitions'][str(spNum)]['subset_score_type']:
                        subset_score_type += self.spartDict['spartitions'][str(spNum)]['subset_score_type'] +' / '
                else:
                    if hasSubset_score_type:
                        subset_score_type += '? / '
                #spartition_score_type
                if checkKey(self.spartDict['spartitions'][str(spNum)], 'spartition_score_type'):
                    hasSpartition_score_type = True
                    if self.spartDict['spartitions'][str(spNum)]['spartition_score_type']:
                        spartition_score_type += self.spartDict['spartitions'][str(spNum)]['spartition_score_type'] +' / '
                else:
                    if hasSpartition_score_type:
                        spartition_score_type += '? / '

                #individual_score_type
                # spartition_score_type
                if checkKey(self.spartDict['spartitions'][str(spNum)], 'individual_score_type'):
                    hasIndividual_score_type = True
                    if self.spartDict['spartitions'][str(spNum)]['individual_score_type']:
                        individual_score_type += self.spartDict['spartitions'][str(spNum)]['individual_score_type'] + ' / '
                else:
                    if hasIndividual_score_type:
                        individual_score_type += '? / '
                #count subsets
                indiCount = 0
                for subNum, val in self.spartDict['spartitions'][str(spNum)]['subsets'].items():
                    if subNum.isnumeric():
                        subCountDict[spNum] = 1 + subCountDict.get(spNum, 0)
                        if checkKey(self.spartDict['spartitions'][str(spNum)]['subsets'][subNum], 'score'):
                            if self.spartDict['spartitions'][str(spNum)]['subsets'][subNum]['score']:
                                n_subsets_scores += f"{str(self.spartDict['spartitions'][str(spNum)]['subsets'][subNum]['score']) + ', '}"
                            else:
                                n_subsets_scores += "?, "
                        for _ in self.spartDict['spartitions'][str(spNum)]['subsets'][subNum]['individuals'].keys():
                            indiCount += 1
                n_subsets_strings.append(f"{str(subCountDict[spNum])}: {n_subsets_scores}")
                n_subsets_scores = ""
                n_individuals += str(indiCount) + ' / '

            for subCount in range(1, len(subCountDict) + 1):
                n_subsets += n_subsets_strings[subCount-1][:-2]+ ' / '

            f.write(f'\n\nn_spartitions = {n_spartition[:-3]};')
            f.write(f'\n\nn_individuals = {n_individuals[:-3]};')

            f.write(f'\n\nn_subsets = {n_subsets[:-3]};')
            if hasSubset_score_type:
                f.write(f'\n\nsubset_score_type = {subset_score_type[:-3]};')
            if hasSpartition_score_type:
                f.write(f'\n\nspartition_score_type = {spartition_score_type[:-3]};')
            if hasIndividual_score_type:
                f.write(f'\n\nindividual_score_type = {individual_score_type[:-3]};')
            f.write(f'\n\nindividual_assignment = ')

            for indiName in self.spartDict["individuals"].keys():
                inSub = []
                for spartition in self.spartDict['spartitions'].values():
                    for num, subset in spartition['subsets'].items():
                        individuals = subset['individuals']
                        if indiName in individuals:
                            inSub.append(str(num))
                            break
                f.write(f'\n{indiName} : {" / ".join(inSub)}')
            f.write(' ;')

            def has_individual_scores():
                for spartition in self.spartDict['spartitions'].values():
                    for subset in spartition['subsets'].values():
                        for tags in subset['individuals'].values():
                            if 'score' in tags:
                                return True
                return False

            if has_individual_scores():
                f.write(f'\n\nindividual_scores = ')

                for indiName in self.spartDict["individuals"].keys():
                    inSub = []
                    for spartition in self.spartDict['spartitions'].values():
                        for subset in spartition['subsets'].values():
                            individuals = subset['individuals']
                            if indiName in individuals:
                                tags = individuals[indiName]
                                score = tags.get('score', None)
                                score = score or '?'
                                inSub.append(str(score))
                                break
                    f.write(f'\n{indiName} : {" / ".join(inSub)}')
                f.write(' ;')

            f.write('\nend;')
            f.close()

    def addIndividual(self, individualName: str, **kwargs) -> None:
        """Add a new individual. Extra information (locality, voucher etc.)
        is passed as keyword arguments."""
        self.spartDict['individuals'][individualName] = {}
        for key, val in kwargs.items():
            self.spartDict['individuals'][individualName][key] = val

    def addSpartition(self, label: str, **kwargs) -> None:
        """Add a new spartition. Extra information (score, type etc.)
        is passed as keyword arguments."""
        spartitionsTags = {'spartitionScore': 'spartition_score',
                           'spartitionScoreType': 'spartition_score_type',
                           'individualScoreType': 'individual_score_type',
                           'subsetScoreType': 'subset_score_type'}

        sparitionNumber = len(self.spartDict['spartitions']) + 1

        self.spartDict['spartitions'][str(sparitionNumber)] = {}
        self.spartDict['spartitions'][str(sparitionNumber)]['subsets'] = {}
        self.spartDict['spartitions'][str(sparitionNumber)]['label'] = label

        for spNum in range(1, sparitionNumber):
            if checkKey(self.spartDict['spartitions'][str(spNum)], 'spartition_score'):
                    self.spartDict['spartitions'][str(sparitionNumber)]['spartition_score'] = None

        for k, v in kwargs.items():
            if k in spartitionsTags:
                k = spartitionsTags[k]
            self.spartDict['spartitions'][str(sparitionNumber)][k] = v


    def addSubset(self, spartition: str, subsetLabel: str, **kwargs) -> None:
        """Add a new subset to the given spartition. Extra information
        (score, taxon name etc.) is passed as keyword arguments."""
        for spartitionRemark in self.spartDict['spartitions'].keys():
            for spartitionName in self.spartDict['spartitions'][spartitionRemark].keys():
                if checkKey(self.spartDict['spartitions'][spartitionRemark], 'label') and not spartition == self.spartDict['spartitions'][spartitionRemark]['label']:
                    continue
                if not spartitionName == 'subsets':
                    continue
                self.spartDict['spartitions'][spartitionRemark]['subsets'][subsetLabel] = {}
                for subs in self.spartDict['spartitions'][spartitionRemark]['subsets'].keys():
                    if checkKey(self.spartDict['spartitions'][spartitionRemark]['subsets'][subs], 'score'):
                        self.spartDict['spartitions'][spartitionRemark]['subsets'][subsetLabel]['score'] = None
                self.spartDict['spartitions'][spartitionRemark]['subsets'][subsetLabel]['individuals'] = {}
                for key, val in kwargs.items():
                    self.spartDict['spartitions'][spartitionRemark]['subsets'][subsetLabel][key] = val

    def addSubsetIndividual(self, spartitionLabel: str, subsetLabel: str, individual: str, **kwargs) -> None:
        """Add an existing individual to the subset of given spartition.
        Extra information (score etc.) is passed as keyword arguments."""
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        spartition['subsets'][subsetLabel]['individuals'][individual] = {}
        spartition['subsets'][subsetLabel]['individuals'][individual] = kwargs

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
        return {}

    def getIndividualLatlon(self, id: str) -> tuple[float, float] or None:
        """Returns latlons information about the given individual id"""
        if checkKey(self.spartDict['individuals'], id):
            if checkKey(self.spartDict['individuals'][id], 'latitude') and checkKey(self.spartDict['individuals'][id], 'longitude'):
                return (self.spartDict['individuals'][id]['latitude'], self.spartDict['individuals'][id]['longitude'])
            if checkKey(self.spartDict['individuals'][id], 'locality'):
                locality = self.getLatlonData(self.spartDict['individuals'][id]['locality'])
                return (locality['latitude'], locality['longitude'])
        return None

    def getLatlon(self) -> iter[str]:
        """Returns a list with the ids of each latlon"""
        for latlon in self.spartDict['latlons'].keys():
            yield latlon

    def getLatlonData(self, id: str) -> dict[str, object]:
        """Returns extra information about the given latlon id"""
        if checkKey(self.spartDict['latlons'], id):
            return self.spartDict['latlons'][id]
        return {}

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

        spartData = {}
        for spartition in self.spartDict['spartitions'].keys():
            if not self.spartDict['spartitions'][spartition]['label'] == label:
                continue
            for tag in self.spartDict['spartitions'][spartition].keys():
                if tag not in ['subsets', 'concordances', 'label', 'remarks']:
                    spartData[tag] = self.spartDict['spartitions'][spartition][tag]

        return spartData

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

    def getSubsetData(self, spartition: str, subset: str) -> dict[str, object]:
        """Returns extra information about the given subset"""
        spartData = {}
        for spartitionName in self.spartDict['spartitions'].keys():
            if not self.spartDict['spartitions'][spartitionName]['label'] == spartition:
                continue
            for subsetLabel in self.spartDict['spartitions'][spartitionName]['subsets'].keys():
                if subsetLabel == subset:
                    for tag, val in self.spartDict['spartitions'][spartitionName]['subsets'][subsetLabel].items():
                        if tag not in ['individuals']:
                            spartData[tag] = val
        return spartData

    def getSubsetIndividualData(self, spartition: str, subset: str, individual: str) -> dict[str, object]:
        """Returns extra information about the given individual
        associated with the given subset."""
        """Returns extra information about the given subset"""
        for spartitionName in self.spartDict['spartitions'].keys():
            if not self.spartDict['spartitions'][spartitionName]['label'] == spartition:
                continue
            return self.spartDict['spartitions'][spartitionName]['subsets'][subset]['individuals'][individual]
        raise Exception('No data present')

    def getSpartitionScore(self, spartitionLabel: str) -> float:
        spartition = self.getSpartitionFromLabel(spartitionLabel)

        score = spartition.get('spartition_score')
        return score

        # return spartition['spartition_score']

    def getSubsetScore(self, spartition: str, subset: str) -> float:
        suScore = self.getSpartitionFromLabel(spartition)['subsets'][subset].get('score')
        return suScore

    def getSubsetIndividualScore(self, spartition: str, subset: str, individual: str) -> float:
        return self.getSpartitionFromLabel(spartition)['subsets'][subset]['individuals'][individual].get('score')

    def getSpartitionScoreType(self, spartitionLabel: str) -> str:
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        scoreType = spartition.get('spartition_score_type')
        return scoreType

    def getSubsetScoreType(self, spartition: str) -> str:
        suScore = self.getSpartitionFromLabel(spartition).get('subset_score_type')
        return suScore

    def getSubsetIndividualScoreType(self, spartition: str) -> str:
        return self.getSpartitionFromLabel(spartition).get('individual_score_type')

    @property
    def project_name(self) -> str:
        return self.spartDict['project_name']

    @project_name.setter
    def project_name(self, name: str):
        self.spartDict['project_name'] = name

    @property
    def date(self) -> datetime:
        string = self.spartDict['date']
        return datetime.fromisoformat(string)

    @date.setter
    def date(self, date: datetime):
        self.spartDict['date'] = date.isoformat()

    def getSpartitionFromLabel(self, spartitionLabel):
        for spartitionRemark, spartition in self.spartDict['spartitions'].items():
            if checkKey(spartition, 'label') and spartition['label'] == spartitionLabel:
                return spartition
        return None


class SpartParser:

    def __init__(self, spartFile):
        self.spartFile = spartFile
        self.spartDict = {}
        self.tree = ET.parse(self.spartFile)
        self.root = self.tree.getroot()

    def getProjectinfo(self):
        self.spartDict["project_name"] = self.root.find("project_name").text
        self.spartDict["date"] = self.root.find("date").text

    def getIndividuals(self):
        individuals = {}
        for individual in self.root.findall('individuals/individual'):
            id = individual.get('id')
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
        spartitionsTags = {'spartitionScore' : 'spartition_score', 'spartitionScoreType': 'spartition_score_type', 'individualScoreType' : 'individual_score_type', 'subsetScoreType': 'subset_score_type'}
        spartitions = {}
        spartition_num = 1
        for spartition in self.root.findall('spartitions/spartition'):
            remarks = spartition.find('remarks')
            spartition_dict = {}
            spartition_dict['remarks'] = remarks.text
            spartition_dict['subsets'] = {}
            spartition_dict['concordances']= {}
            spartition_dict['concordances']['concordance'] = {}

            for index, val in spartition.attrib.items():
                if checkKey(spartitionsTags, index):
                    if index == 'spartitionScore':
                        val = float(val)
                    spartition_dict[spartitionsTags[index]] = val
                else:
                    spartition_dict[index] = val

            for subset in spartition.findall('subsets/subset'):
                subset_dict = {}
                subset_dict['individuals'] = {}

                #Subset
                for index, val in subset.attrib.items():
                    if index == 'label':
                        continue
                    if index =='score':
                        val = float(val)
                    subset_dict[index] = val

                #Subset individuals
                for individual in subset.findall('individual'):
                    individual_dict = {}
                    for index, val in individual.attrib.items():
                        if index == 'ref':
                            continue
                        if index == 'score':
                            val = float(val)
                        individual_dict[index] = val

                    individual_id = individual.get('ref')
                    subset_dict['individuals'][individual_id] = individual_dict

                label = subset.get('label')
                spartition_dict['subsets'][label] = subset_dict

            for concordances in spartition.findall('concordances/concordance'):
                label = concordances.attrib['label']
                spartition_dict['concordances']['concordance'][label] = {}
                date = concordances.find('date')
                concordantsubsets = concordances.findall('concordantsubsets')
                spartition_dict['concordances']['concordance'][label]['date'] = date.text
                spartition_dict['concordances']['concordance'][label]['concordantsubsets'] = []
                for index, val in concordances.attrib.items():
                    if index == 'label':
                        continue
                    spartition_dict['concordances']['concordance'][label][index] = val

                for subset in concordantsubsets:
                    spartition_dict['concordances']['concordance'][label]['concordantsubsets'].append(subset.attrib['subsetnumber'])

            spartitions[str(spartition_num)] = spartition_dict
            spartition_num += 1

        self.spartDict['spartitions'] = spartitions
        return spartitions

    def generateData(self):
        self.getProjectinfo()
        self.getIndividuals()
        self.getSpartitions()
        self.getLatLon()
        self.getSequences()
        return self.spartDict


class SpartParserXML:

    def __init__(self, spartFile):
        self.spartFile = spartFile
        self.spartDict = {}

    def generateData(self):
        self.tokenizer = ET.iterparse(self.spartFile, events=('start', 'end'))
        self.parseRoot()
        return self.spartDict

    def parseRoot(self):
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('start', 'project_name'):
                self.parseProjectName(element)
            if (event, token) == ('start', 'date'):
                self.parseDate(element)
            if (event, token) == ('start', 'individuals'):
                self.parseIndividuals()
            if (event, token) == ('start', 'spartitions'):
                self.parseSpartitions()
            if (event, token) == ('start', 'latlon'):
                self.parseLatLon()
            element.clear()

    def parseProjectName(self, element):
        self.spartDict['project_name'] = element.text
        element.clear()

    def parseDate(self, element):
        self.spartDict['date'] = element.text
        element.clear()

    def parseIndividuals(self):
        self.spartDict['individuals'] = {}
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('end', 'individuals'):
                break
            elif (event, token) == ('start', 'individual'):
                self.parseIndividual(element)
            element.clear()

    def parseIndividual(self, element):
        id = element.get('id')
        elementDict = self.mapLatLonKeys(element, 'id')
        self.spartDict['individuals'][id] = elementDict

    def parseSpartitions(self):
        self.spartDict['spartitions'] = {}
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('end', 'spartitions'):
                break
            elif (event, token) == ('start', 'spartition'):
                self.parseSpartition(element)
            print(self.spartDict['spartitions'])
            element.clear()

    def parseSpartition(self, elem):
        sparitionNumber = str(len(self.spartDict['spartitions']) + 1)
        self.spartDict['spartitions'][sparitionNumber] = elem.attrib
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('end', 'spartition'):
                break
            if (event, token) == ('start', 'remarks'):
                self.parseRemark(element, sparitionNumber)
            if (event, token) == ('start', 'subsets'):
                self.parseSubsets(sparitionNumber)
            element.clear()

    def parseSubsets(self, sparitionNumber):
        self.spartDict['spartitions'][sparitionNumber]['subsets'] = {}
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('end', 'subsets'):
                break
            elif (event, token) == ('start', 'subset'):
                self.parseSubset(element, sparitionNumber)
            element.clear()

    def parseSubset(self, elem, sparitionNumber):
        subsetNumber = elem.get('label')
        self.spartDict['spartitions'][sparitionNumber]['subsets'][subsetNumber] = self.mapLatLonKeys(elem, 'label')
        self.spartDict['spartitions'][sparitionNumber]['subsets'][subsetNumber]['individuals'] = {}
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('end', 'subset'):
                break
            elif (event, token) == ('start', 'individual'):
                self.parseSubsetIndividual(element, sparitionNumber, subsetNumber)
            element.clear()


    def parseSubsetIndividual(self, element, sparitionNumber, subsetNumber):
        id = element.get('ref')
        elementDict = self.mapLatLonKeys(element, 'ref')
        self.spartDict['spartitions'][sparitionNumber]['subsets'][subsetNumber]['individuals'][id] = elementDict

    def parseRemark(self, element, sparitionNumber):
        self.spartDict['spartitions'][sparitionNumber]['remarks'] = element.text
        element.clear()
        
    def parseLatLon(self):
        self.spartDict['latlons'] = {}
        for event, element in self.tokenizer:
            token = element.tag
            if (event, token) == ('end', 'latlon'):
                break
            elif (event, token) == ('start', 'coordinates'):
                self.parseCoordinates(element)
            element.clear()

    def parseCoordinates(self, element):
        id = element.get('locality')
        elementDict = self.mapLatLonKeys(element, 'locality')
        elementDict['latitude'] = float(elementDict['latitude'])

        synonyms = elementDict.get('synonyms','').split(';')
        for synonym in synonyms:
            self.spartDict['latlons'][synonym] = elementDict
        self.spartDict['latlons'][id] = elementDict

    def mapLatLonKeys(self, element, id):
        mappingsDict = {'alt': 'altitude', 'lat': 'latitude', 'lon': 'longitude', 'synonym': 'synonyms'}
        elementDict = {}
        for key, val in without_keys(element.attrib, id).items():
            if key in mappingsDict:
                key = mappingsDict[key]
            if key in ['altitude', 'longitude', 'latitude']:
                val = float(val)
            elementDict[key] = val
        return elementDict


class SpartParserRegular:

    def __init__(self, fileName):
        self.fileName = fileName
        self.spartDict = {}
        with open(fileName, 'r+') as f:
            self.spartFile = f.readlines()
        self.keysDict = {}
        self.individualAssignments = {}
        self.individualScores = {}

    def getKeys(self):
        for line in self.spartFile:
            n = line.split('=')
            if len(n)> 1:
                self.keysDict[n[0].strip().lower()] = n[0].strip()

    def getProjectinfo(self):
        for line in self.spartFile:
            prjectName = re.search(self.keysDict['project_name'] + r'\s?=\s?([^;]+);' , line)
            if prjectName:
                self.spartDict["project_name"] = prjectName.group(1)
            date = re.search(self.keysDict['date'] + r'\s?=\s?([^;]+);' , line)
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

    def getindividualScores(self):
        #individuals
        startIndi = False
        count = 0
        if not checkKey(self.keysDict, 'individual_scores'):
            return False
        for line in self.spartFile:
            result = re.search(f'({self.keysDict["individual_scores"]})', line)
            if result:
                startIndi = True
                continue
            if startIndi and line.strip() == ';':
                startIndi = False
                break
            if startIndi and line.strip()[-1] == ';':
                indi = line.strip().split(':')
                self.individualScores[indi[0].strip()] = indi[1][:-1].strip()
                break
            elif startIndi:
                indi = line.strip().split(':')
                self.individualScores[indi[0].strip()] = indi[1].strip()

        return True

    def getSpartitions(self):
        self.spartDict['spartitions'] = {}
        spartList = []
        subsetCounttList = []
        subset_score_type_list = []
        spartition_score_type_list = []
        individual_score_type_list = []
        numOfspart = '0'
        individualScoresPresent = False
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

            #subset_score_type
            if checkKey(self.keysDict,"subset_score_type"):
                result = re.search(f'({self.keysDict["subset_score_type"]}.*)', line)
                if result:
                    getSubScoresType = result.group(1).split("=")[1].strip()
                    typesList =  getSubScoresType.strip().split('/')
                    for scoreType in typesList:
                        type = scoreType.strip()
                        subset_score_type_list.append(type)

                    if subset_score_type_list[-1][-1] == ';':
                        subset_score_type_list[-1] = subset_score_type_list[-1][:-1]

            #spartition_score_type
            if checkKey(self.keysDict, "spartition_score_type"):
                result = re.search(f'({self.keysDict["spartition_score_type"]}.*)', line)
                if result:
                    getSpartitionScoresType = result.group(1).split("=")[1].strip()
                    typesList =  getSpartitionScoresType.strip().split('/')
                    for scoreType in typesList:
                        type = scoreType.strip()
                        spartition_score_type_list.append(type)

                    if spartition_score_type_list[-1][-1] == ';':
                        spartition_score_type_list[-1] = spartition_score_type_list[-1][:-1]

            #individual_score_type
            if checkKey(self.keysDict, "individual_score_type"):
                result = re.search(f'({self.keysDict["individual_score_type"]}.*)', line)
                if result:
                    getIndividualScoresType = result.group(1).split("=")[1].strip()
                    typesList =  getIndividualScoresType.strip().split('/')
                    for scoreType in typesList:
                        type = scoreType.strip()
                        individual_score_type_list.append(type)

                    if individual_score_type_list[-1][-1] == ';':
                        individual_score_type_list[-1] = individual_score_type_list[-1][:-1]

        if self.getindividualScores():
            individualScoresPresent = True

        for spartion in range(1,numOfspart+1):
            spartionNumber = str(spartion)     #n2w(spartion) + ' spartition'
            spartionLabel = spartList[spartion-1].strip().split(',')
            self.spartDict['spartitions'][spartionNumber] = {'label' : spartionLabel[0]}

            #score types
            if not len(subset_score_type_list) < 1:
                if subset_score_type_list[spartion-1].strip() == '?':
                    self.spartDict['spartitions'][spartionNumber]['subset_score_type'] = None
                else:
                    self.spartDict['spartitions'][spartionNumber]['subset_score_type'] = subset_score_type_list[spartion-1].strip()

            if not len(spartition_score_type_list) < 1:
                if spartition_score_type_list[spartion-1].strip() == '?':
                    self.spartDict['spartitions'][spartionNumber]['spartition_score_type'] = None
                else:
                    self.spartDict['spartitions'][spartionNumber]['spartition_score_type'] = spartition_score_type_list[spartion-1].strip()

            if not len(individual_score_type_list) < 1:
                if individual_score_type_list[spartion-1].strip() == '?':
                    self.spartDict['spartitions'][spartionNumber]['individual_score_type'] = None
                else:
                    self.spartDict['spartitions'][spartionNumber]['individual_score_type'] = individual_score_type_list[spartion-1].strip()

            #spartition score

            if spartionLabel[-1].strip() == '?':
                self.spartDict['spartitions'][spartionNumber]['spartition_score'] = None
            elif len(spartionLabel) > 1:
                self.spartDict['spartitions'][spartionNumber]['spartition_score'] = float(spartionLabel[1].strip())

            count = 0
            #create subsets
            self.spartDict['spartitions'][spartionNumber]['subsets'] = {}
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
                    if not scoreList[count-1].strip() == '?':
                        self.spartDict['spartitions'][spartionNumber]['subsets'][str(count)]['score'] = float(scoreList[count-1].strip())
                    else:
                        self.spartDict['spartitions'][spartionNumber]['subsets'][str(count)]['score'] = None

                self.spartDict['spartitions'][spartionNumber]['subsets'][str(count)]['individuals'] = {}


        for subsets in self.individualAssignments.keys():
            subsetList = self.individualAssignments[subsets].split('/')
            if individualScoresPresent:
                scoresList = self.individualScores[subsets].split('/')
            count = 0
            for subset in range(1,numOfspart+1):
                spartionNumber = str(subset)     #n2w(subset) + ' spartition'
                self.spartDict['spartitions'][spartionNumber]['subsets'][str(subsetList[count].strip())]['individuals'][subsets] = {}
                if individualScoresPresent:
                    if not scoresList[count].strip() == '?':
                        self.spartDict['spartitions'][spartionNumber]['subsets'][str(subsetList[count].strip())]['individuals'][subsets]['score'] = float(scoresList[count].strip())
                    else:
                        self.spartDict['spartitions'][spartionNumber]['subsets'][str(subsetList[count].strip())]['individuals'][subsets]['score'] = None
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


def is_path_xml(path: Path) -> bool:
    try:
        ET.parse(path)
        return True
    except ET.ParseError:
        return False


def main():
    path = Path(argv[1])
    spart = Spart.fromPath(path)
    from json import dumps
    return dumps(spart.spartDict)


def demo():
    demoDir = Path("demo")
    demoDir.mkdir(exist_ok=True)

    exmDir = Path("examples")
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    for src in exmDir.iterdir():
        spart = Spart.fromPath(src)
        dest_xml = demoDir / f'{src.name}.{timestamp}.xml'
        spart.toXML(dest_xml)
        dest_mat = demoDir / f'{src.name}.{timestamp}.spart'
        spart.toMatricial(dest_mat)


if __name__ == '__main__':
    spart = Spart.fromPath('../../../tests/data/scores.spart')
    demoDir = Path("demo")
    dest_mat = demoDir / f't.spart'
    spart.toMatricial(dest_mat)
