#!/usr/bin/env python3

from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto

import pytest

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class SpartType(Enum):
    Matricial = auto()
    XML = auto()


@dataclass
class ConversionTest:
    input: str
    output: str
    type: SpartType


test_data = [
    ConversionTest('simple.spart', 'simple.xml', SpartType.XML),
    ConversionTest('simple.xml', 'simple.spart', SpartType.Matricial),
    ]


def assert_eq_files(file1: Path, file2: Path) -> None:
    assert file1.read_text() == file2.read_text()


def convert(input, output, type: SpartType):
    if type is SpartType.Matricial:
        with open(output, 'w') as file:
            file.write('MATRICIAL\n')
    elif type is SpartType.XML:
        with open(output, 'w') as file:
            file.write('XML\n')


@pytest.mark.parametrize("test", test_data)
def test_read_write(test: ConversionTest, tmp_path: Path) -> None:
    input_path = TEST_DATA_DIR / test.input
    output_path = TEST_DATA_DIR / test.output
    test_path = tmp_path / test.output
    convert(input_path, test_path, test.type)
    assert_eq_files(test_path, output_path)
