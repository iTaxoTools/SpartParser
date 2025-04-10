from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from sys import argv
from xml.sax.saxutils import XMLGenerator, quoteattr


class Spart:
    """Holds a list of individuals, spartitions and their subsets"""

    def __init__(self, spartDict: dict = None):
        """Create a new empty dataset by default"""
        if spartDict is None:
            self.spartDict = {}
            self.spartDict["project_name"] = ""
            self.spartDict["date"] = ""
            self.spartDict["individuals"] = {}
            self.spartDict["spartitions"] = {}
            self.spartDict["locations"] = {}
            self.spartDict["location_synonyms"] = {}
        else:
            self.spartDict = spartDict

    @classmethod
    def fromMatricial(cls, path: Path) -> Spart:
        """Parse a matricial spart file and return a Spart instance"""
        parser = SpartParserMatricial(str(path))
        spartDict = parser.generateData()
        return cls(spartDict)

    @classmethod
    def fromXML(cls, path: Path) -> Spart:
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
        writer = SpartWriterXML()
        writer.toPath(self, path)

    def toMatricial(self, path: Path) -> None:
        """Convert Spart instance to matricial spart file"""

        # Creating spart file with given path
        with open(path, "w") as f:
            f.write("begin spart;")
            numSpartitions = len(self.spartDict["spartitions"])
            subCountDict = {}
            if checkKey(self.spartDict, "project_name"):
                f.write(f'\n\nproject_name = {self.spartDict["project_name"]};')
            if checkKey(self.spartDict, "date"):
                f.write(f'\n\ndate = {self.spartDict["date"]};')

            n_spartition = f"{numSpartitions} : "
            n_individuals = ""
            n_subsets = ""
            n_subsets_scores = ""
            subset_score_type = ""
            spartition_score_type = ""
            individual_score_type = ""
            hasSubset_score_type = False
            hasSpartition_score_type = False
            hasIndividual_score_type = False
            n_subsets_strings = []

            for spNum in range(1, numSpartitions + 1):
                # label
                if checkKey(self.spartDict["spartitions"][str(spNum)], "label"):
                    # spartition_score
                    if checkKey(
                        self.spartDict["spartitions"][str(spNum)], "spartitionScore"
                    ):
                        n_spartition += (
                            self.spartDict["spartitions"][str(spNum)]["label"] + ", "
                        )
                        if (
                            self.spartDict["spartitions"][str(spNum)]["spartitionScore"]
                            is not None
                        ):
                            n_spartition += f"{str(self.spartDict['spartitions'][str(spNum)]['spartitionScore'])}  / "
                        else:
                            n_spartition += "? / "
                    else:
                        n_spartition += (
                            self.spartDict["spartitions"][str(spNum)]["label"] + " / "
                        )
                # subset_score_type

                if checkKey(
                    self.spartDict["spartitions"][str(spNum)], "subsetScoreType"
                ):
                    hasSubset_score_type = True
                    if self.spartDict["spartitions"][str(spNum)]["subsetScoreType"]:
                        subset_score_type += (
                            self.spartDict["spartitions"][str(spNum)]["subsetScoreType"]
                            + " / "
                        )
                else:
                    if hasSubset_score_type:
                        subset_score_type += "? / "
                # spartition_score_type
                if checkKey(
                    self.spartDict["spartitions"][str(spNum)], "spartitionScoreType"
                ):
                    hasSpartition_score_type = True
                    if self.spartDict["spartitions"][str(spNum)]["spartitionScoreType"]:
                        spartition_score_type += (
                            self.spartDict["spartitions"][str(spNum)][
                                "spartitionScoreType"
                            ]
                            + " / "
                        )
                else:
                    if hasSpartition_score_type:
                        spartition_score_type += "? / "

                # individual_score_type
                # spartition_score_type
                if checkKey(
                    self.spartDict["spartitions"][str(spNum)], "individualScoreType"
                ):
                    hasIndividual_score_type = True
                    if self.spartDict["spartitions"][str(spNum)]["individualScoreType"]:
                        individual_score_type += (
                            self.spartDict["spartitions"][str(spNum)][
                                "individualScoreType"
                            ]
                            + " / "
                        )
                else:
                    if hasIndividual_score_type:
                        individual_score_type += "? / "
                # count subsets
                indiCount = 0
                for subNum, val in self.spartDict["spartitions"][str(spNum)][
                    "subsets"
                ].items():
                    if subNum.isnumeric():
                        subCountDict[spNum] = 1 + subCountDict.get(spNum, 0)
                        if checkKey(
                            self.spartDict["spartitions"][str(spNum)]["subsets"][
                                subNum
                            ],
                            "score",
                        ):
                            if self.spartDict["spartitions"][str(spNum)]["subsets"][
                                subNum
                            ]["score"]:
                                n_subsets_scores += f"{str(self.spartDict['spartitions'][str(spNum)]['subsets'][subNum]['score']) + ', '}"
                            else:
                                n_subsets_scores += "?, "
                        for _ in self.spartDict["spartitions"][str(spNum)]["subsets"][
                            subNum
                        ]["individuals"].keys():
                            indiCount += 1
                n_subsets_strings.append(
                    f"{str(subCountDict[spNum])}: {n_subsets_scores}"
                )
                n_subsets_scores = ""
                n_individuals += str(indiCount) + " / "

            for subCount in range(1, len(subCountDict) + 1):
                n_subsets += n_subsets_strings[subCount - 1][:-2] + " / "

            f.write(f"\n\nn_spartitions = {n_spartition[:-3]};")
            f.write(f"\n\nn_individuals = {n_individuals[:-3]};")

            f.write(f"\n\nn_subsets = {n_subsets[:-3]};")
            if hasSubset_score_type:
                f.write(f"\n\nsubset_score_type = {subset_score_type[:-3]};")
            if hasSpartition_score_type:
                f.write(f"\n\nspartition_score_type = {spartition_score_type[:-3]};")
            if hasIndividual_score_type:
                f.write(f"\n\nindividual_score_type = {individual_score_type[:-3]};")
            f.write("\n\nindividual_assignment = ")

            for indiName in self.spartDict["individuals"].keys():
                inSub = []
                for spartition in self.spartDict["spartitions"].values():
                    for num, subset in spartition["subsets"].items():
                        individuals = subset["individuals"]
                        if indiName in individuals:
                            inSub.append(str(num))
                            break
                f.write(f'\n{indiName} : {" / ".join(inSub)}')
            f.write(" ;")

            def has_individual_scores():
                for spartition in self.spartDict["spartitions"].values():
                    for subset in spartition["subsets"].values():
                        for tags in subset["individuals"].values():
                            if "score" in tags:
                                return True
                return False

            if has_individual_scores():
                f.write("\n\nindividual_score = ")

                for indiName in self.spartDict["individuals"].keys():
                    inSub = []
                    for spartition in self.spartDict["spartitions"].values():
                        for subset in spartition["subsets"].values():
                            individuals = subset["individuals"]
                            if indiName in individuals:
                                tags = individuals[indiName]
                                score = tags.get("score", None)
                                score = score or "?"
                                inSub.append(str(score))
                                break
                    f.write(f'\n{indiName} : {" / ".join(inSub)}')
                f.write(" ;")

            f.write("\nend;")
            f.close()

    def addIndividual(self, id: str, **kwargs) -> None:
        """Add a new individual. Extra information (locality, voucher etc.)
        is passed as keyword arguments."""
        self.spartDict["individuals"][id] = {"types": {}, **kwargs}

    def addIndividualType(self, individual: str, status: str, **kwargs) -> None:
        """Add a new type with the provided status to the individual with the
        provided id. Extra information (nameBearingStatus, originalNameUsage
        etc.) is passed as keyword arguments."""
        self.spartDict["individuals"][individual]["types"][status] = kwargs

    def addSpartition(self, label: str, remarks: str = None, **kwargs) -> None:
        """Add a new spartition. Extra information (score, type etc.)
        is passed as keyword arguments."""
        spartitionsTags = {
            "spartition_score": "spartitionScore",
            "spartition_score_type": "spartitionScoreType",
            "individual_score_type": "individualScoreType",
            "subset_score_type": "subsetScoreType",
        }

        spartitionNumber = len(self.spartDict["spartitions"]) + 1

        self.spartDict["spartitions"][str(spartitionNumber)] = {}
        self.spartDict["spartitions"][str(spartitionNumber)]["subsets"] = {}
        self.spartDict["spartitions"][str(spartitionNumber)]["concordances"] = {}
        self.spartDict["spartitions"][str(spartitionNumber)]["label"] = label
        self.spartDict["spartitions"][str(spartitionNumber)]["remarks"] = remarks

        for spNum in range(1, spartitionNumber):
            if checkKey(self.spartDict["spartitions"][str(spNum)], "spartitionScore"):
                self.spartDict["spartitions"][str(spartitionNumber)][
                    "spartitionScore"
                ] = None

        for k, v in kwargs.items():
            if k in spartitionsTags:
                k = spartitionsTags[k]
            self.spartDict["spartitions"][str(spartitionNumber)][k] = v

    def addSubset(self, spartition: str, subsetLabel: str, **kwargs) -> None:
        """Add a new subset to the given spartition. Extra information
        (score, taxon name etc.) is passed as keyword arguments."""
        for spartitionRemark in self.spartDict["spartitions"].keys():
            for spartitionName in self.spartDict["spartitions"][
                spartitionRemark
            ].keys():
                if (
                    checkKey(self.spartDict["spartitions"][spartitionRemark], "label")
                    and not spartition
                    == self.spartDict["spartitions"][spartitionRemark]["label"]
                ):
                    continue
                if not spartitionName == "subsets":
                    continue
                self.spartDict["spartitions"][spartitionRemark]["subsets"][
                    subsetLabel
                ] = {}
                for subs in self.spartDict["spartitions"][spartitionRemark][
                    "subsets"
                ].keys():
                    if checkKey(
                        self.spartDict["spartitions"][spartitionRemark]["subsets"][
                            subs
                        ],
                        "score",
                    ):
                        self.spartDict["spartitions"][spartitionRemark]["subsets"][
                            subsetLabel
                        ]["score"] = None
                self.spartDict["spartitions"][spartitionRemark]["subsets"][subsetLabel][
                    "individuals"
                ] = {}
                for key, val in kwargs.items():
                    self.spartDict["spartitions"][spartitionRemark]["subsets"][
                        subsetLabel
                    ][key] = val

    def addSubsetIndividual(
        self, spartitionLabel: str, subsetLabel: str, individual: str, **kwargs
    ) -> None:
        """Add an existing individual to the subset of given spartition.
        Extra information (score etc.) is passed as keyword arguments."""
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        spartition["subsets"][subsetLabel]["individuals"][individual] = {}
        spartition["subsets"][subsetLabel]["individuals"][individual] = kwargs

    def addLocation(self, locality: str, synonyms: list[str] = [], **kwargs) -> None:
        """Add a new location. Extra information (latitude, longitude etc.)
        is passed as keyword arguments."""
        self.spartDict["locations"][locality] = kwargs
        for synonym in synonyms:
            self.spartDict["location_synonyms"][synonym] = locality

    def addConcordance(
        self, spartitionLabel: str, concordanceLabel: str, **kwargs
    ) -> None:
        """Add a new concordance to the given spartition. Extra information
        (evidence type, date etc.) is passed as keyword arguments."""
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        concordances = spartition["concordances"]
        concordances[concordanceLabel] = dict(kwargs)
        concordances[concordanceLabel]["limits"] = []

    def addConcordantLimit(
        self,
        spartitionLabel: str,
        concordanceLabel: str,
        subsetnumberA: str,
        subsetnumberB: str,
        NIndividualsSubsetA: str,
        NIndividualsSubsetB: str,
        concordanceSupport: str | float | bool,
    ) -> None:
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        concordance = spartition["concordances"][concordanceLabel]
        (
            self._check_concordance_support_type(
                concordanceSupport, concordance["evidenceDiscriminationDataType"]
            ),
        )
        limit = dict(
            subsetnumberA=subsetnumberA,
            subsetnumberB=subsetnumberB,
            NIndividualsSubsetA=NIndividualsSubsetA,
            NIndividualsSubsetB=NIndividualsSubsetB,
            concordanceSupport=concordanceSupport,
        )
        concordance["limits"].append(limit)

    @classmethod
    def _check_concordance_support_type(cls, support: str | float | bool, type: str):
        if type == "Boolean" and not isinstance(support, bool):
            raise Exception(f"Unexpected support type for {support}: expected bool")
        float_types = ["Continuous", "Percentage", "Proportion"]
        if type in float_types and not isinstance(support, float):
            raise Exception(f"Unexpected support type for {support}: expected float")

    def getIndividuals(self) -> list[str]:
        """Returns a list with the ids of each individual"""
        individuals_list = []
        for individual in self.spartDict["individuals"].keys():
            individuals_list.append(individual)

        return individuals_list

    def getIndividualData(self, id: str) -> dict[str, object]:
        """Returns extra information about the given individual id"""
        if checkKey(self.spartDict["individuals"], id):
            return without_keys(self.spartDict["individuals"][id], "types")
        return {}

    def getIndividualLatLon(self, id: str) -> tuple[float, float] | None:
        """Returns lat/lon information about the given individual id"""
        individual = self.spartDict["individuals"][id]
        lat = individual.get("decimalLatitude", None)
        lon = individual.get("decimalLongitude", None)
        if lat is not None and lon is not None:
            return (lat, lon)
        locality = individual.get("locality", None)
        if not locality:
            return None
        locality = self.spartDict["location_synonyms"].get(locality, locality)
        location = self.spartDict["locations"][locality]
        lat = location.get("decimalLatitude", None)
        lon = location.get("decimalLongitude", None)
        return (lat, lon)

    def getIndividualTypes(self, id: str) -> iter[str]:
        """Returns extra information about the given individual types"""
        individualTypes_list = []
        for types in self.spartDict["individuals"][id]["types"].keys():
            individualTypes_list.append(types)
        return individualTypes_list

    def getIndividualTypeData(self, id: str, type: str) -> dict[str, str]:
        if checkKey(self.spartDict["individuals"], id):
            if checkKey(self.spartDict["individuals"][id]["types"], type):
                return self.spartDict["individuals"][id]["types"][type]
        return {}

    def getLocations(self) -> iter[str]:
        """Returns a list with the ids of each location"""
        for latlon in self.spartDict["locations"].keys():
            yield latlon

    def getLocationData(self, id: str) -> dict[str, object]:
        """Returns extra information about the given latlon id"""
        if checkKey(self.spartDict["locations"], id):
            return self.spartDict["locations"][id]
        return {}

    def getSpartitions(self) -> list[str]:
        """Returns a list with the labels of each spartition"""
        labels_list = []
        for spartition in self.spartDict["spartitions"].keys():
            for tag in self.spartDict["spartitions"][spartition].keys():
                if tag == "label":
                    labels_list.append(self.spartDict["spartitions"][spartition][tag])
        return labels_list

    def getSpartitionData(self, label: str) -> dict[str, object]:
        """Returns extra information about the given spartition"""
        spartData = {}
        for spartition in self.spartDict["spartitions"].keys():
            if not self.spartDict["spartitions"][spartition]["label"] == label:
                continue
            for tag in self.spartDict["spartitions"][spartition].keys():
                if tag not in ["subsets", "concordances", "label", "remarks"]:
                    spartData[tag] = self.spartDict["spartitions"][spartition][tag]
        return spartData

    def getSpartitionRemarks(self, label: str) -> str:
        for spartition in self.spartDict["spartitions"].keys():
            if not self.spartDict["spartitions"][spartition]["label"] == label:
                continue
            return self.spartDict["spartitions"][spartition]["remarks"]

    def getSpartitionConcordances(self, label: str) -> list[str]:
        """Returns a list with the labels of all concordances of the given spartition"""
        spartition = self.getSpartitionFromLabel(label)
        return list(spartition["concordances"].keys())

    def getConcordanceData(
        self, spartition: str, concordance: str
    ) -> dict[str, object]:
        """Returns extra information about the given concordance"""
        spartition = self.getSpartitionFromLabel(spartition)
        data = spartition["concordances"][concordance]
        data = dict(data)
        data.pop("limits")
        return data

    def getConcordantLimits(self, spartition: str, concordance: str) -> list[dict]:
        """Returns a list of all concordant limits contained in the spartition
        and concordance specified by the given labels."""
        spartition = self.getSpartitionFromLabel(spartition)
        data = spartition["concordances"][concordance]
        return list(data["limits"])

    def getSpartitionSubsets(self, label: str) -> list[str]:
        """Returns a list with the labels of all subsets of the given spartition"""
        spartition = self.getSpartitionFromLabel(label)
        return list(spartition["subsets"].keys())

    def getSubsetIndividuals(self, spartitionLabel: str, subsetNum: str) -> list[str]:
        """Returns a list of all individuals contained in the spartition
        and subset specified by the given labels."""
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        data = spartition["subsets"][subsetNum]
        return list(data["individuals"].keys())

    def getSubsetData(self, spartition: str, subset: str) -> dict[str, object]:
        """Returns extra information about the given subset"""
        spartition = self.getSpartitionFromLabel(spartition)
        data = spartition["subsets"][subset]
        data = dict(data)
        data.pop("individuals")
        return data

    def getSubsetIndividualData(
        self, spartition: str, subset: str, individual: str
    ) -> dict[str, object]:
        """Returns extra information about the given individual
        when associated with the given subset."""
        for spartitionName in self.spartDict["spartitions"].keys():
            if not self.spartDict["spartitions"][spartitionName]["label"] == spartition:
                continue
            return self.spartDict["spartitions"][spartitionName]["subsets"][subset][
                "individuals"
            ][individual]
        raise Exception("No data present")

    def getSpartitionScore(self, spartitionLabel: str) -> float:
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        score = spartition.get("spartitionScore")
        return score

    def getSubsetScore(self, spartition: str, subset: str) -> float:
        suScore = self.getSpartitionFromLabel(spartition)["subsets"][subset].get(
            "score"
        )
        return suScore

    def getSubsetIndividualScore(
        self, spartition: str, subset: str, individual: str
    ) -> float:
        return self.getSpartitionFromLabel(spartition)["subsets"][subset][
            "individuals"
        ][individual].get("score")

    def getSpartitionScoreType(self, spartitionLabel: str) -> str:
        spartition = self.getSpartitionFromLabel(spartitionLabel)
        scoreType = spartition.get("spartitionScoreType")
        return scoreType

    def getSubsetScoreType(self, spartition: str) -> str:
        suScore = self.getSpartitionFromLabel(spartition).get("subsetScoreType")
        return suScore

    def getSubsetIndividualScoreType(self, spartition: str) -> str:
        return self.getSpartitionFromLabel(spartition).get("individualScoreType")

    @property
    def project_name(self) -> str:
        return self.spartDict["project_name"]

    @project_name.setter
    def project_name(self, name: str):
        self.spartDict["project_name"] = name

    @property
    def date(self) -> datetime:
        string = self.spartDict["date"]
        if string:
            return datetime.fromisoformat(string)
        return None

    @date.setter
    def date(self, date: datetime):
        self.spartDict["date"] = date.isoformat()

    def getSpartitionFromLabel(self, spartitionLabel: str) -> dict | None:
        """Since indexing is not being done with label for some reason..."""
        for spartitionRemark, spartition in self.spartDict["spartitions"].items():
            if checkKey(spartition, "label") and spartition["label"] == spartitionLabel:
                return spartition
        raise Exception(f"Spartition not found: {repr(spartitionLabel)}")


class SpartParserXML:
    castMap = {
        "decimalLatitude": float,
        "decimalLongitude": float,
        "elevation": float,
        "measurementAccuracy": int,
        "elevationAccuracy": int,
        "spartitionScore": float,
        "score": float,
    }

    keyMap = {
        "project_name": [],
        "date": [],
        "individuals": [],
        "individual": [],
        "id": [],
        "locality": [],
        "decimalLatitude": ["latitude", "lat"],
        "decimalLongitude": ["longitude", "lon"],
        "elevation": ["altitude", "alt"],
        "measurementAccuracy": [],
        "elevationAccuracy": [],
        "type": [],
        "status": [],
        "nameBearingStatus": [],
        "namePublishedInYear": [],
        "scientificNameAuthorship": [],
        "originalNameUsage": [],
        "verbatimTypeLocality": [],
        "spartitions": [],
        "spartition": [],
        "label": [],
        "spartitionScore": [],
        "spartitionScoreType": [],
        "subsetScoreType": [],
        "subsetScoreSource": [],
        "individualScoreType": [],
        "individualScoreSource": [],
        "remarks": [],
        "subsets": [],
        "subset": [],
        "ref": [],
        "locations": [],
        "coordinates": [],
        "synonyms": ["synonym"],
    }

    keyMapInverse = {
        synonym.lower(): key
        for key, synonyms in keyMap.items()
        for synonym in synonyms + [key.lower()]
    }

    @classmethod
    def translate(cls, key: str):
        return cls.keyMapInverse.get(key.lower(), key)

    @classmethod
    def cast(cls, key: str, value):
        return cls.castMap.get(key, str)(value)

    @classmethod
    def processElement(cls, element: ET.Element, key: str = None):
        attributes = {cls.translate(k): v for k, v in element.attrib.items()}
        attributes = {k: cls.cast(k, v) for k, v in attributes.items()}
        keyValue = attributes.pop(key, None)
        return keyValue, attributes

    def __init__(self, spartFile):
        self.spartFile = spartFile
        self.spartDict = {}

    def generateData(self):
        self.tokenizer = ET.iterparse(self.spartFile, events=("start", "end"))
        self.parseRoot()
        return self.spartDict

    def parseRoot(self):
        self.spartDict["project_name"] = ""
        self.spartDict["date"] = ""
        self.spartDict["individuals"] = {}
        self.spartDict["spartitions"] = {}
        self.spartDict["locations"] = {}
        self.spartDict["location_synonyms"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("start", "project_name"):
                self.parseProjectName(element)
            if (event, token) == ("start", "date"):
                self.parseProjectDate(element)
            if (event, token) == ("start", "individuals"):
                self.parseIndividuals()
            if (event, token) == ("start", "spartitions"):
                self.parseSpartitions()
            if (event, token) == ("start", "locations"):
                self.parseLocations()
            element.clear()

    def parseProjectName(self, element):
        self.spartDict["project_name"] = element.text
        element.clear()

    def parseProjectDate(self, element):
        self.spartDict["date"] = element.text
        element.clear()

    def parseIndividuals(self):
        self.spartDict["individuals"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, self.translate(token)) == ("end", "individuals"):
                break
            elif (event, token) == ("start", "individual"):
                self.parseIndividual(element)
            element.clear()

    def parseIndividual(self, element):
        id, attrs = self.processElement(element, "id")
        self.spartDict["individuals"][id] = attrs
        self.spartDict["individuals"][id]["types"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "individual"):
                break
            elif (event, token) == ("start", "type"):
                self.parseIndividualType(element, id)
            element.clear()

    def parseIndividualType(self, element, id: str):
        status, attrs = self.processElement(element, "status")
        self.spartDict["individuals"][id]["types"][status] = attrs

    def parseSpartitions(self):
        self.spartDict["spartitions"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "spartitions"):
                break
            elif (event, token) == ("start", "spartition"):
                self.parseSpartition(element)
            element.clear()

    def parseSpartition(self, element):
        _, attrs = self.processElement(element)
        spartitionNumber = str(len(self.spartDict["spartitions"]) + 1)
        self.spartDict["spartitions"][spartitionNumber] = attrs
        self.spartDict["spartitions"][spartitionNumber]["remarks"] = None
        self.spartDict["spartitions"][spartitionNumber]["subsets"] = {}
        self.spartDict["spartitions"][spartitionNumber]["concordances"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "spartition"):
                break
            if (event, token) == ("start", "remarks"):
                self.parseRemark(element, spartitionNumber)
            if (event, token) == ("start", "subsets"):
                self.parseSubsets(spartitionNumber)
            if (event, token) == ("start", "concordances"):
                self.parseConcordances(spartitionNumber)
            element.clear()

    def parseSubsets(self, spartition):
        self.spartDict["spartitions"][spartition]["subsets"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "subsets"):
                break
            elif (event, token) == ("start", "subset"):
                self.parseSubset(element, spartition)
            element.clear()

    def parseSubset(self, element, spartition):
        label, attrs = self.processElement(element, "label")
        self.spartDict["spartitions"][spartition]["subsets"][label] = attrs
        self.spartDict["spartitions"][spartition]["subsets"][label]["individuals"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "subset"):
                break
            elif (event, token) == ("start", "individual"):
                self.parseSubsetIndividual(element, spartition, label)
            element.clear()

    def parseSubsetIndividual(self, element, spartition, subset):
        ref, attrs = self.processElement(element, "ref")
        self.spartDict["spartitions"][spartition]["subsets"][subset]["individuals"][
            ref
        ] = attrs

    def parseConcordances(self, spartition):
        self.spartDict["spartitions"][spartition]["concordances"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "concordances"):
                break
            elif (event, token) == ("start", "concordance"):
                self.parseConcordance(element, spartition)
            element.clear()

    def parseConcordance(self, element, spartition):
        concordance, attrs = self.processElement(element, "evidenceName")
        self.spartDict["spartitions"][spartition]["concordances"][concordance] = attrs
        self.spartDict["spartitions"][spartition]["concordances"][concordance][
            "limits"
        ] = []
        cast_type = str
        if attrs["evidenceDiscriminationDataType"] == "Boolean":
            cast_type = lambda x: x.lower() == "yes"  # noqa
        elif attrs["evidenceDiscriminationDataType"] in [
            "Continuous",
            "Percentage",
            "Proportion",
        ]:
            cast_type = float
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "concordance"):
                break
            if (event, token) == ("start", "analysis"):
                self.parseConcordanceAnalysis(element, spartition, concordance)
            if (event, token) == ("start", "date"):
                self.parseConcordanceDate(element, spartition, concordance)
            elif (event, token) == ("start", "concordantlimit"):
                self.parseConcordantLimit(element, spartition, concordance, cast_type)
            element.clear()

    def parseConcordanceAnalysis(self, element, spartition, concordance):
        analysis, _ = self.processElement(element, "name")
        self.spartDict["spartitions"][spartition]["concordances"][concordance][
            "analysis"
        ] = analysis

    def parseConcordanceDate(self, element, spartition, concordance):
        date = datetime.fromisoformat(element.text)
        self.spartDict["spartitions"][spartition]["concordances"][concordance][
            "date"
        ] = date

    def parseConcordantLimit(self, element, spartition, concordance, cast_type):
        _, attrs = self.processElement(element)
        attrs["concordanceSupport"] = cast_type(attrs["concordanceSupport"])
        self.spartDict["spartitions"][spartition]["concordances"][concordance][
            "limits"
        ].append(attrs)

    def parseRemark(self, element, spartition):
        self.spartDict["spartitions"][spartition]["remarks"] = element.text

    def parseLocations(self):
        self.spartDict["locations"] = {}
        self.spartDict["location_synonyms"] = {}
        for event, element in self.tokenizer:
            token = self.translate(element.tag)
            if (event, token) == ("end", "locations"):
                break
            elif (event, token) == ("start", "coordinates"):
                self.parseCoordinates(element)
            element.clear()

    def parseCoordinates(self, element):
        id, attrs = self.processElement(element, "locality")
        synonyms = attrs.get("synonyms", "").split(";")
        for synonym in synonyms:
            if synonym:
                self.spartDict["location_synonyms"][synonym] = id
        self.spartDict["locations"][id] = attrs


class SpartParserMatricial:
    def __init__(self, fileName):
        self.fileName = fileName
        self.spartDict = {
            "individuals": {},
            "spartitions": {},
            "locations": {},
        }
        with open(fileName, "r+") as f:
            self.spartFile = f.readlines()
        self.keysDict = {}
        self.individualAssignments = {}
        self.individualScores = {}

    def getKeys(self):
        for line in self.spartFile:
            n = line.split("=")
            if len(n) > 1:
                self.keysDict[n[0].strip().lower()] = n[0].strip()

    def getProjectinfo(self):
        for line in self.spartFile:
            prjectName = re.search(
                self.keysDict["project_name"] + r"\s?=\s?([^;]+);", line
            )
            if prjectName:
                self.spartDict["project_name"] = prjectName.group(1)
            date = re.search(self.keysDict["date"] + r"\s?=\s?([^;]+);", line)
            if date:
                self.spartDict["date"] = date.group(1)

    def getIndividuals(self):
        self.spartDict["individuals"] = {}
        # individuals
        startIndi = False
        for line in self.spartFile:
            result = re.search(f'({self.keysDict["individual_assignment"]})', line)
            if result:
                startIndi = True
                continue
            if startIndi and line.strip() == ";":
                startIndi = False
                break
            if startIndi and line.strip()[-1] == ";":
                indi = line.strip().split(":")
                self.spartDict["individuals"][indi[0].strip()] = {"types": {}}
                self.individualAssignments[indi[0].strip()] = indi[1][:-1].strip()
                break
            elif startIndi:
                indi = line.strip().split(":")
                self.spartDict["individuals"][indi[0].strip()] = {"types": {}}
                self.individualAssignments[indi[0].strip()] = indi[1].strip()

        return self.spartDict

    def getIndividualScores(self):
        # individuals
        startIndi = False
        if not checkKey(self.keysDict, "individual_score"):
            return False
        for line in self.spartFile:
            result = re.search(f'({self.keysDict["individual_score"]})', line)
            if result:
                startIndi = True
                continue
            if startIndi and line.strip() == ";":
                startIndi = False
                break
            if startIndi and line.strip()[-1] == ";":
                indi = line.strip().split(":")
                self.individualScores[indi[0].strip()] = indi[1][:-1].strip()
                break
            elif startIndi:
                indi = line.strip().split(":")
                self.individualScores[indi[0].strip()] = indi[1].strip()

        return True

    def getSpartitions(self):
        self.spartDict["spartitions"] = {}
        spartList = []
        subsetCounttList = []
        subset_score_type_list = []
        spartition_score_type_list = []
        individual_score_type_list = []
        numOfspart = "0"
        individualScoresPresent = False
        for line in self.spartFile:
            # subsets
            result = re.search(f'({self.keysDict["n_subsets"]}.*)', line)
            if result:
                getSubsets = result.group(1).split("=")[1].strip()
                counttList = getSubsets.strip().split("/")
                for scores in counttList:
                    score = scores.strip().split(":")
                    subsetCounttList.append(
                        [score[0], score[1] if score[-1] != score[0] else ""]
                    )
            # spartitions
            result = re.search(f'({self.keysDict["n_spartitions"]}.*)', line)
            if result:
                getSubsets = result.group(1).split("=")[1].strip()
                subset = getSubsets.split(":")
                spartList = subset[1].strip().split("/")
                if spartList[-1][-1] == ";":
                    spartList[-1] = spartList[-1][:-1]
                numOfspart = int(subset[0])

            # subset_score_type
            if checkKey(self.keysDict, "subset_score_type"):
                result = re.search(f'({self.keysDict["subset_score_type"]}.*)', line)
                if result:
                    getSubScoresType = result.group(1).split("=")[1].strip()
                    typesList = getSubScoresType.strip().split("/")
                    for scoreType in typesList:
                        type = scoreType.strip()
                        subset_score_type_list.append(type)

                    if subset_score_type_list[-1][-1] == ";":
                        subset_score_type_list[-1] = subset_score_type_list[-1][:-1]

            # spartition_score_type
            if checkKey(self.keysDict, "spartition_score_type"):
                result = re.search(
                    f'({self.keysDict["spartition_score_type"]}.*)', line
                )
                if result:
                    getSpartitionScoresType = result.group(1).split("=")[1].strip()
                    typesList = getSpartitionScoresType.strip().split("/")
                    for scoreType in typesList:
                        type = scoreType.strip()
                        spartition_score_type_list.append(type)

                    if spartition_score_type_list[-1][-1] == ";":
                        spartition_score_type_list[-1] = spartition_score_type_list[-1][
                            :-1
                        ]

            # individual_score_type
            if checkKey(self.keysDict, "individual_score_type"):
                result = re.search(
                    f'({self.keysDict["individual_score_type"]}.*)', line
                )
                if result:
                    getIndividualScoresType = result.group(1).split("=")[1].strip()
                    typesList = getIndividualScoresType.strip().split("/")
                    for scoreType in typesList:
                        type = scoreType.strip()
                        individual_score_type_list.append(type)

                    if individual_score_type_list[-1][-1] == ";":
                        individual_score_type_list[-1] = individual_score_type_list[-1][
                            :-1
                        ]

        if self.getIndividualScores():
            individualScoresPresent = True

        for spartion in range(1, numOfspart + 1):
            spartionNumber = str(spartion)  # n2w(spartion) + ' spartition'
            spartionLabel = spartList[spartion - 1].strip().split(",")
            self.spartDict["spartitions"][spartionNumber] = {
                "label": spartionLabel[0],
                "remarks": None,
                "concordances": {},
            }

            # score types
            if not len(subset_score_type_list) < 1:
                if subset_score_type_list[spartion - 1].strip() == "?":
                    self.spartDict["spartitions"][spartionNumber][
                        "subsetScoreType"
                    ] = None
                else:
                    self.spartDict["spartitions"][spartionNumber][
                        "subsetScoreType"
                    ] = subset_score_type_list[spartion - 1].strip()

            if not len(spartition_score_type_list) < 1:
                if spartition_score_type_list[spartion - 1].strip() == "?":
                    self.spartDict["spartitions"][spartionNumber][
                        "spartitionScoreType"
                    ] = None
                else:
                    self.spartDict["spartitions"][spartionNumber][
                        "spartitionScoreType"
                    ] = spartition_score_type_list[spartion - 1].strip()

            if not len(individual_score_type_list) < 1:
                if individual_score_type_list[spartion - 1].strip() == "?":
                    self.spartDict["spartitions"][spartionNumber][
                        "individualScoreType"
                    ] = None
                else:
                    self.spartDict["spartitions"][spartionNumber][
                        "individualScoreType"
                    ] = individual_score_type_list[spartion - 1].strip()

            # spartition score

            if spartionLabel[-1].strip() == "?":
                self.spartDict["spartitions"][spartionNumber]["spartitionScore"] = None
            elif len(spartionLabel) > 1:
                self.spartDict["spartitions"][spartionNumber][
                    "spartitionScore"
                ] = float(spartionLabel[1].strip())

            count = 0
            # create subsets
            self.spartDict["spartitions"][spartionNumber]["subsets"] = {}
            if subsetCounttList[-1][0][-1] == ";":
                subsetCounttList[-1][0] = subsetCounttList[-1][0][:-1]
            for subset in range(int(subsetCounttList[spartion - 1][0].strip())):
                count += 1
                self.spartDict["spartitions"][spartionNumber]["subsets"][
                    str(count)
                ] = {}

            count = 0
            # add subset score
            for subset in range(int(subsetCounttList[spartion - 1][0].strip())):
                count += 1
                if subsetCounttList[spartion - 1][1] != "":
                    scoreList = subsetCounttList[spartion - 1][1].split(",")
                    if scoreList[-1][-1] == ";":
                        scoreList[-1] = scoreList[-1][:-1]
                    if not scoreList[count - 1].strip() == "?":
                        self.spartDict["spartitions"][spartionNumber]["subsets"][
                            str(count)
                        ]["score"] = float(scoreList[count - 1].strip())
                    else:
                        self.spartDict["spartitions"][spartionNumber]["subsets"][
                            str(count)
                        ]["score"] = None

                self.spartDict["spartitions"][spartionNumber]["subsets"][str(count)][
                    "individuals"
                ] = {}

        for subsets in self.individualAssignments.keys():
            subsetList = self.individualAssignments[subsets].split("/")
            if individualScoresPresent:
                scoresList = self.individualScores[subsets].split("/")
            count = 0
            for subset in range(1, numOfspart + 1):
                spartionNumber = str(subset)  # n2w(subset) + ' spartition'
                self.spartDict["spartitions"][spartionNumber]["subsets"][
                    str(subsetList[count].strip())
                ]["individuals"][subsets] = {}
                if individualScoresPresent:
                    if not scoresList[count].strip() == "?":
                        self.spartDict["spartitions"][spartionNumber]["subsets"][
                            str(subsetList[count].strip())
                        ]["individuals"][subsets]["score"] = float(
                            scoresList[count].strip()
                        )
                    else:
                        self.spartDict["spartitions"][spartionNumber]["subsets"][
                            str(subsetList[count].strip())
                        ]["individuals"][subsets]["score"] = None
                count += 1
        return self.spartDict

    def generateData(self):
        self.getKeys()
        self.getProjectinfo()
        self.getIndividuals()
        self.getSpartitions()
        return self.spartDict


class PrettyXMLGenerator(XMLGenerator):
    """Extends the ContentHandler interface"""

    def __init__(
        self, out=None, encoding="iso-8859-1", indent="\t", short_empty_elements=False
    ):
        super().__init__(out, encoding, short_empty_elements)
        self._indent_str = indent
        self._indent_level = 0

    def startDocument(self):
        # self._write(f'<?xml version="1.0" encoding="{self._encoding}"?>\n')
        self._write('<?xml version="1.0" ?>')

    def indent(self, diff=0):
        if diff < 0:
            self._indent_level += diff
        self.ignorableWhitespace("\n")
        self.ignorableWhitespace(self._indent_str * self._indent_level)
        if diff > 0:
            self._indent_level += diff

    def startElement(self, name, attrs=None):
        self.indent(1)
        if not attrs:
            attrs = {}
        super().startElement(name, attrs)

    def endElement(self, name):
        self.indent(-1)
        super().endElement(name)

    def startEndElement(self, name, attrs=None, characters=None):
        self.indent()
        if not attrs:
            attrs = {}
        self._finish_pending_start_element()
        self._write("<" + name)
        for name, value in attrs.items():
            self._write(" %s=%s" % (name, quoteattr(value)))

        if characters:
            self._write(">")
            self.characters(characters)
            super().endElement(name)
        else:
            self._write("/>")


class SpartWriterXML:
    keyMap = {
        "spartition_score": "spartitionScore",
        "spartition_score_type": "spartitionScoreType",
        "individual_score_type": "individualScoreType",
        "subset_score_type": "subsetScoreType",
    }

    def __init__(self):
        self.handler = None
        self.spart = None

    def toPath(self, spart: Spart, path: Path):
        self.spart = spart
        with open(path, "w") as file:
            self.handler = PrettyXMLGenerator(file, "UTF-8", "\t")
            self.handler.startDocument()
            self.writeRoot()
            self.handler.endDocument()

    def writeRoot(self):
        self.handler.startElement("root")
        self.writeProjectInfo()
        self.writeIndividuals()
        self.writeSpartitions()
        self.writeLocations()
        self.handler.endElement("root")

    def writeProjectInfo(self):
        project_name = self.spart.project_name
        if project_name:
            self.handler.startEndElement("project_name", characters=project_name)
        date = self.spart.date
        if date:
            self.handler.startEndElement("date", characters=date.isoformat())

    def writeIndividuals(self):
        self.handler.startElement("individuals")
        for individual in self.spart.getIndividuals():
            self.writeIndividual(individual)
        self.handler.endElement("individuals")

    def writeIndividual(self, individual: str):
        data = self.spart.getIndividualData(individual)
        data = self.formatData(data, "id", individual)
        types = self.spart.getIndividualTypes(individual)
        if not types:
            self.handler.startEndElement("individual", data)
        else:
            self.handler.startElement("individual", data)
            for type in types:
                typeData = self.spart.getIndividualTypeData(individual, type)
                typeData = self.formatData(typeData, "status", type)
                self.handler.startEndElement("type", typeData)
            self.handler.endElement("individual")

    def writeSpartitions(self):
        if not any(self.spart.getSpartitions()):
            return
        self.handler.startElement("spartitions")
        for spartition in self.spart.getSpartitions():
            self.writeSpartition(spartition)
        self.handler.endElement("spartitions")

    def writeSpartition(self, spartition: str):
        data = self.spart.getSpartitionData(spartition)
        data = self.formatData(data, "label", spartition)
        remarks = self.spart.getSpartitionRemarks(spartition)
        self.handler.startElement("spartition", data)
        if remarks:
            self.handler.startEndElement("remarks", characters=remarks)
        self.writeSubsets(spartition)
        self.writeConcordances(spartition)
        self.handler.endElement("spartition")

    def writeSubsets(self, spartition: str):
        if not any(self.spart.getSpartitionSubsets(spartition)):
            return
        self.handler.startElement("subsets")
        for subset in self.spart.getSpartitionSubsets(spartition):
            self.writeSubset(spartition, subset)
        self.handler.endElement("subsets")

    def writeSubset(self, spartition: str, subset: str):
        data = self.spart.getSubsetData(spartition, subset)
        data = self.formatData(data, "label", subset)
        self.handler.startElement("subset", data)
        for individual in self.spart.getSubsetIndividuals(spartition, subset):
            individualData = self.spart.getSubsetIndividualData(
                spartition, subset, individual
            )
            individualData = self.formatData(individualData, "ref", individual)
            self.handler.startEndElement("individual", individualData)
        self.handler.endElement("subset")

    def writeConcordances(self, spartition: str):
        if not any(self.spart.getSpartitionConcordances(spartition)):
            return
        self.handler.startElement("concordances")
        for concordance in self.spart.getSpartitionConcordances(spartition):
            self.writeConcordance(spartition, concordance)
        self.handler.endElement("concordances")

    def writeConcordance(self, spartition: str, concordance: str):
        data = self.spart.getConcordanceData(spartition, concordance)
        if "date" in data:
            data["date"] = data["date"].isoformat()
        data = self.formatData(data, "evidenceName", concordance)
        data_type = data["evidenceDiscriminationDataType"]
        analysis = data.pop("analysis", None)
        date = data.pop("date", None)
        self.handler.startElement("concordance", data)
        if analysis is not None:
            self.handler.startEndElement("analysis", dict(name=analysis))
        if date is not None:
            self.handler.startEndElement("date", characters=date)
        for limit in self.spart.getConcordantLimits(spartition, concordance):
            if data_type == "Boolean":
                limit["concordanceSupport"] = (
                    "Yes" if limit["concordanceSupport"] else "No"
                )
            if data_type in ["Continuous", "Percentage", "Proportion"]:
                limit["concordanceSupport"] = str(limit["concordanceSupport"])
            self.handler.startEndElement("concordantlimit", limit)
        self.handler.endElement("concordance")

    def writeLocations(self):
        if not any(self.spart.getLocations()):
            return
        self.handler.startElement("locations")
        for location in self.spart.getLocations():
            self.writeLocation(location)
        self.handler.endElement("locations")

    def writeLocation(self, location: str):
        data = self.spart.getLocationData(location)
        data = self.formatData(data, "locality", location)
        self.handler.startEndElement("coordinates", data)

    def formatData(self, data: dict, key: str, value: str):
        data = {self.keyMap.get(k, k): str(v) for k, v in data.items() if v is not None}
        return {key: value, **data}


def n2w(n):
    num2words = {
        1: "First",
        2: "Second",
        3: "Third",
        4: "Fourth",
        5: "Fifth",
        6: "Sixth",
        7: "Seventh",
        8: "Eight",
        9: "Ninth",
        10: "Tenth",
        11: "Eleventh",
        12: "Twelfth",
        13: "Thirteenth",
        14: "Fourteenth",
        15: "Fifteenth",
        16: "Sixteenth",
        17: "Seventeenth",
        18: "Eighteenth",
        19: "Nineteenth",
        20: "Twentieth|Twenty",
        30: "Thirtieth|Thirty",
        40: "Fortieth|Forty",
        50: "Fiftieth|Fifty",
        60: "Sixtieth|Sixty",
        70: "Seventieth|Seventy",
        80: "Eightieth|Eighty",
        90: "Ninetieth|Ninety",
        0: "Zero",
    }
    try:
        num2word = num2words[n].split("|")[0]
        return num2word
    except KeyError:
        try:
            num2word = num2words[n - n % 10].split("|")[1]
            return num2word + "-" + num2words[n % 10].lower()
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
        for _, element in ET.iterparse(path):
            element.clear()
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
    timestamp = datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%f")

    print(f"Iterating '{str(exmDir.resolve())}'")
    for src in exmDir.iterdir():
        print(f"Parsing {src.name}")
        spart = Spart.fromPath(src)
        dest_xml = demoDir / f"{src.name}.{timestamp}.xml"
        spart.toXML(dest_xml)
        dest_mat = demoDir / f"{src.name}.{timestamp}.spart"
        spart.toMatricial(dest_mat)
    print(f"Done, results in '{str(demoDir.resolve())}'")
