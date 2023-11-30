# SpartParser

[![GitHub - Windows](https://github.com/iTaxoTools/SpartParser/actions/workflows/windows.yml/badge.svg)](
    https://github.com/iTaxoTools/SpartParser/actions/workflows/windows.yml)
[![GitHub - Tests](https://github.com/iTaxoTools/SpartParser/actions/workflows/test.yml/badge.svg)](
    https://github.com/iTaxoTools/SpartParser/actions/workflows/test.yml)
[![GitHub - Deploy](https://github.com/iTaxoTools/SpartParser/actions/workflows/deploy.yml/badge.svg)](
    https://github.com/iTaxoTools/SpartParser/actions/workflows/deploy.yml)

Parse, edit and write data in the SPART and SPART-XML file formats.

Includes a GUI for converting between the two formats.


## Installing from source

To install just the parser, please use:

```
pip install git+https://github.com/iTaxoTools/SpartParser.git
```

To install for development with GUI dependencies:

```
git clone https://github.com/iTaxoTools/SpartParser.git
cd SpartParser
pip install -e ".[dev,gui]" -f packages.html
```

## Usage

Most of the functionality is included in the Spart class. Use the class methods to open, edit and write data in the Spart file format.

```
from itaxotools.spart_parser import Spart
spart = Spart.fromXML("examples/spart.xml")

spartitions = spart.getSpartitions()
print(spartitions)
subsets = spart.getSpartitionSubsets(spartitions[0])
print(subsets)
individuals = spart.getSubsetIndividuals(spartitions[0], subsets[0])
print(individuals)

spart.addIndividual("new_specimen")
spart.addSubsetIndividual(spartitions[0], subsets[0], "new_specimen")
spart.addSubsetIndividual(spartitions[1], subsets[1], "new_specimen")
spart.toMatricial("converted_copy.spart")
```

For more details, refer to the [Spart class definition](src/itaxotools/spart_parser/main.py), as well as the [scripts](scripts) and [examples](examples) folders.
