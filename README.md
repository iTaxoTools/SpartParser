# SpartParser

[![PyPI - Version](https://img.shields.io/pypi/v/itaxotools-spart-parser)](
    https://pypi.org/project/itaxotools-spart-parser)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/itaxotools-spart-parser)](
    https://pypi.org/project/itaxotools-spart-parser)
[![PyPI - License](https://img.shields.io/pypi/l/itaxotools-spart-parser)](
    https://pypi.org/project/itaxotools-spart-parser)
[![GitHub - Tests](https://img.shields.io/github/actions/workflow/status/iTaxoTools/itt-spart-parser/test.yml?label=tests)](
    https://github.com/iTaxoTools/SpartParser/actions/workflows/test.yml)
[![GitHub - Windows](https://img.shields.io/github/actions/workflow/status/iTaxoTools/SpartParser/windows.yml?logo=windows&logoColor=white&label=windows)](
    https://github.com/iTaxoTools/SpartParser/actions/workflows/windows.yml)

Parse, edit and write data in the SPART and SPART-XML file formats.

Includes a GUI for converting between the two formats.


## Installation

PyInstaller is available on PyPI. You can install it through `pip`:

```
pip install itaxotools-spart-parser
```

## Usage

Most of the functionality is included in the Spart class. Use the class methods
to open, edit and write data in the Spart file format.

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

For more details, refer to the [Spart class definition](src/itaxotools/spart_parser/main.py),
as well as the [scripts](scripts) and [examples](examples) folders.

# Demo GUI

A graphical interface is included for converting between SPART and SPART-XML.

Install with the optional GUI dependencies:
```
pip install itaxotools-spart-parser
SpartParserGui
```

Or download and run the Windows executable from the
[latest release](https://github.com/iTaxoTools/SpartParser/releases/latest).
