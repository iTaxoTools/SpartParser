#!/usr/bin/env python3

from pathlib import Path
from dataclasses import dataclass
from typing import Callable
from enum import Enum, auto

import pytest
import re

from itaxotools.spart_parser import Spart

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class SpartType(Enum):
    Matricial = auto()
    XML = auto()


@dataclass
class ConversionTest:
    input: str
    output: str
    parser: Callable
    writer: Callable


test_data = [
    ConversionTest('simple.spart', 'simple.xml', Spart.fromMatricial, Spart.toXML),
    ConversionTest('simple.xml', 'simple.spart', Spart.fromXML, Spart.toMatricial),
    ]


def assert_eq_files(file1: Path, file2: Path) -> None:
    regex = re.compile(r'[\s]')
    text1 = file1.read_text()
    text2 = file2.read_text()
    text1 = regex.sub('', text1)
    text2 = regex.sub('', text2)
    assert text1 == text2


@pytest.mark.parametrize("test", test_data)
def test_read_write(test: ConversionTest, tmp_path: Path) -> None:
    input_path = TEST_DATA_DIR / test.input
    output_path = TEST_DATA_DIR / test.output
    test_path = tmp_path / test.output
    spart = test.parser(input_path)
    test.writer(spart, test_path)
    assert_eq_files(test_path, output_path)
