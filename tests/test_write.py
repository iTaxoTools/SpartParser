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

    spart.addSpartition('spartition_1', source='M', remarks='First spartition')
    spart.addSubset('spartition_1', '1', taxon='taxon_1_1')
    spart.addSubsetIndividual('spartition_1', '1', 'individual_1', score="1.1")
    spart.addSubset('spartition_1', '2', taxon='taxon_1_2')
    spart.addSubsetIndividual('spartition_1', '2', 'individual_2', score="1.2")
    spart.addSubset('spartition_1', '3', taxon='taxon_1_3')
    spart.addSubsetIndividual('spartition_1', '3', 'individual_3', score="1.3")

    spart.addSpartition('spartition_2', source='N', remarks='Second spartition')
    spart.addSubset('spartition_2', '1', taxon='taxon_2_1')
    spart.addSubsetIndividual('spartition_2', '1', 'individual_1', score="2.1")
    spart.addSubsetIndividual('spartition_2', '1', 'individual_2', score="2.2")
    spart.addSubset('spartition_2', '2', taxon='taxon_2_2')
    spart.addSubsetIndividual('spartition_2', '2', 'individual_3', score="2.3")

    spart.addSpartition('spartition_3', source='O', remarks='Third spartition')
    spart.addSubset('spartition_3', '1', taxon='taxon_3_1')
    spart.addSubsetIndividual('spartition_3', '1', 'individual_1', score="3.1")
    spart.addSubsetIndividual('spartition_3', '1', 'individual_2', score="3.2")
    spart.addSubsetIndividual('spartition_3', '1', 'individual_3', score="3.3")

    return spart

def spart_scores():
    spart = Spart()
    spart.project_name = 'scores_test'
    spart.date = datetime.datetime(2022, 10, 2, 12, 0, 0)

    spart.addIndividual('individual_1')
    spart.addIndividual('individual_2')
    spart.addIndividual('individual_3')

    spart.addSpartition('spartition_1', spartitionScore=0.1)
    spart.addSubset('spartition_1', '1', score=1.1)
    spart.addSubsetIndividual('spartition_1', '1', 'individual_1', score=1.1)
    spart.addSubset('spartition_1', '2', score=1.2)
    spart.addSubsetIndividual('spartition_1', '2', 'individual_2', score=2.1)
    spart.addSubset('spartition_1', '3')
    spart.addSubsetIndividual('spartition_1', '3', 'individual_3', score=3.1)

    spart.addSpartition('spartition_2', spartitionScore=0.2)
    spart.addSubset('spartition_2', '1', score=2.1)
    spart.addSubsetIndividual('spartition_2', '1', 'individual_1', score=1.2)
    spart.addSubsetIndividual('spartition_2', '1', 'individual_2', score=2.2)
    spart.addSubset('spartition_2', '2', score=2.2)
    spart.addSubsetIndividual('spartition_2', '2', 'individual_3', score=3.2)

    spart.addSpartition('spartition_3')
    spart.addSubset('spartition_3', '1', score=3.1)
    spart.addSubsetIndividual('spartition_3', '1', 'individual_1', score=None)
    spart.addSubsetIndividual('spartition_3', '1', 'individual_2', score=2.3)
    spart.addSubsetIndividual('spartition_3', '1', 'individual_3', score=3.3)

    return spart


def spart_scores_type():
    spart = Spart()
    spart.project_name = 'score_type_test'
    spart.date = datetime.datetime(2022, 10, 2, 12, 0, 0)

    spart.addIndividual('individual_1')
    spart.addIndividual('individual_2')
    spart.addIndividual('individual_3')

    spart.addSpartition(
        'spartition_1',
        individual_score_type='individual_score_1',
        spartition_score_type='spartition_score_1',
        subset_score_type='subset_score_1',
        )
    spart.addSubset('spartition_1', '1')
    spart.addSubsetIndividual('spartition_1', '1', 'individual_1')
    spart.addSubset('spartition_1', '2')
    spart.addSubsetIndividual('spartition_1', '2', 'individual_2')
    spart.addSubset('spartition_1', '3')
    spart.addSubsetIndividual('spartition_1', '3', 'individual_3')

    spart.addSpartition(
        'spartition_2',
        individual_score_type='individual_score_2',
        spartition_score_type='spartition_score_2',
        subset_score_type='subset_score_2',
        )
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

test_data = [
    WriteTest('simple.xml', Spart.toXML, spart_simple),
    WriteTest('simple.spart', Spart.toMatricial, spart_simple),
    WriteTest('tagged.xml', Spart.toXML, spart_tagged),
    WriteTest('scores.spart', Spart.toMatricial, spart_scores),
    WriteTest('scores.xml', Spart.toXML, spart_scores),
    WriteTest('scores_type.spart', Spart.toMatricial, spart_scores_type),
    WriteTest('scores_type.xml', Spart.toXML, spart_scores_type),
    ]


@pytest.mark.parametrize("test", test_data)
def test_write(test: WriteTest, tmp_path: Path) -> None:
    output_path = TEST_DATA_DIR / test.output
    test_path = tmp_path / test.output
    spart = test.generator()
    test.writer(spart, test_path)
    assert_eq_files(test_path, output_path)
