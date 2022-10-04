#!/usr/bin/env python3

from pathlib import Path
from dataclasses import dataclass
from typing import Callable
import pytest
import datetime

from utility import assert_eq_files

from itaxotools.spart_parser import Spart

TEST_DATA_DIR = Path(__file__).parent / 'data'


@dataclass
class WriteTest:
    output: str
    writer: Callable
    generator: Callable


def spart_simple():
    spart = Spart()
    spart.project_name = 'simple_test'
    spart.date = datetime.datetime(2022, 10, 2, 12, 0, 0)

    spart.addIndividual('individual_1')
    spart.addIndividual('individual_2')
    spart.addIndividual('individual_3')

    spart.addSpartition('spartition_1')
    spart.addSubset('spartition_1', '1')
    spart.addSubsetIndividual('spartition_1', '1', 'individual_1')
    spart.addSubset('spartition_1', '2')
    spart.addSubsetIndividual('spartition_1', '2', 'individual_2')
    spart.addSubset('spartition_1', '3')
    spart.addSubsetIndividual('spartition_1', '3', 'individual_3')

    spart.addSpartition('spartition_2')
    spart.addSubset('spartition_2', '1')
    spart.addSubsetIndividual('spartition_2', '1', 'individual_1')
    spart.addSubsetIndividual('spartition_2', '1', 'individual_2')
    spart.addSubset('spartition_2', '2')
    spart.addSubsetIndividual('spartition_2', '2', 'individual_3')

    spart.addSpartition('spartition_3')
    spart.addSubset('spartition_3', '1')
    spart.addSubsetIndividual('spartition_3', '1', 'individual_1')
    spart.addSubsetIndividual('spartition_3', '1', 'individual_2')
    spart.addSubsetIndividual('spartition_3', '1', 'individual_3')

    return spart


def spart_tagged():
    spart = Spart()
    spart.project_name = 'tagged_test'
    spart.date = datetime.datetime(2022, 10, 2, 12, 0, 0)

    spart.addIndividual('individual_1', locality='A', voucher='X')
    spart.addIndividual('individual_2', locality='B')
    spart.addIndividual('individual_3', locality='C')

    spart.addSpartition('spartition_1', source='M')
    spart.addSubset('spartition_1', '1', taxon='taxon_1_1')
    spart.addSubsetIndividual('spartition_1', '1', 'individual_1', score="1.1")
    spart.addSubset('spartition_1', '2', taxon='taxon_1_2')
    spart.addSubsetIndividual('spartition_1', '2', 'individual_2', score="1.2")
    spart.addSubset('spartition_1', '3', taxon='taxon_1_3')
    spart.addSubsetIndividual('spartition_1', '3', 'individual_3', score="1.3")

    spart.addSpartition('spartition_2', source='N')
    spart.addSubset('spartition_2', '1', taxon='taxon_2_1')
    spart.addSubsetIndividual('spartition_2', '1', 'individual_1', score="2.1")
    spart.addSubsetIndividual('spartition_2', '1', 'individual_2', score="2.2")
    spart.addSubset('spartition_2', '2', taxon='taxon_2_2')
    spart.addSubsetIndividual('spartition_2', '2', 'individual_3', score="2.3")

    spart.addSpartition('spartition_3', source='O')
    spart.addSubset('spartition_3', '1', taxon='taxon_3_1')
    spart.addSubsetIndividual('spartition_3', '1', 'individual_1', score="3.1")
    spart.addSubsetIndividual('spartition_3', '1', 'individual_2', score="3.2")
    spart.addSubsetIndividual('spartition_3', '1', 'individual_3', score="3.3")

    return spart


test_data = [
    WriteTest('simple.xml', Spart.toXML, spart_simple),
    WriteTest('simple.spart', Spart.toMatricial, spart_simple),
    WriteTest('tagged.xml', Spart.toXML, spart_tagged),
    ]


@pytest.mark.parametrize("test", test_data)
def test_write(test: WriteTest, tmp_path: Path) -> None:
    output_path = TEST_DATA_DIR / test.output
    test_path = tmp_path / test.output
    spart = test.generator()
    test.writer(spart, test_path)
    assert_eq_files(test_path, output_path)

