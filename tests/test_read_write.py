#!/usr/bin/env python3

from pathlib import Path
from dataclasses import dataclass
from typing import Callable

import pytest

from utility import assert_eq_files

from itaxotools.spart_parser import Spart

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


@dataclass
class ReadWriteTest:
    input: str
    output: str
    parser: Callable
    writer: Callable


test_data = [
    ReadWriteTest('simple.spart', 'simple.xml', Spart.fromMatricial, Spart.toXML),
    ReadWriteTest('simple.xml', 'simple.spart', Spart.fromXML, Spart.toMatricial),
    ]


@pytest.mark.parametrize("test", test_data)
def test_read_write(test: ReadWriteTest, tmp_path: Path) -> None:
    input_path = TEST_DATA_DIR / test.input
    output_path = TEST_DATA_DIR / test.output
    test_path = tmp_path / test.output
    spart = test.parser(input_path)
    test.writer(spart, test_path)
    assert_eq_files(test_path, output_path)
