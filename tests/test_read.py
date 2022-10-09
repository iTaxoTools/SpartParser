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
class ReadTest:
    input: str
    reader: Callable
    validator: Callable


def spart_simple(spart: Spart):
    assert spart.project_name == 'simple_test'
    assert spart.date == datetime.datetime(2022, 10, 2, 12, 0, 0)

    # Validate individual list

    individuals = spart.getIndividuals()
    assert len(individuals) == 3
    assert 'individual_1' in individuals
    assert 'individual_2' in individuals
    assert 'individual_3' in individuals
    assert not spart.getIndividualData('individual_1')
    assert not spart.getIndividualData('individual_2')
    assert not spart.getIndividualData('individual_3')

    # Validate spartition list

    spartitions = spart.getSpartitions()
    assert len(spartitions) == 3
    assert 'spartition_1' in spartitions
    assert 'spartition_2' in spartitions
    assert 'spartition_3' in spartitions
    assert not spart.getSpartitionData('spartition_1')
    assert not spart.getSpartitionData('spartition_2')
    assert not spart.getSpartitionData('spartition_3')

    # Validate subset lists

    subsets = spart.getSpartitionSubsets('spartition_1')
    assert len(subsets) == 3
    assert '1' in subsets
    assert '2' in subsets
    assert '3' in subsets
    assert not spart.getSubsetData('spartition_1', '1')
    assert not spart.getSubsetData('spartition_1', '2')
    assert not spart.getSubsetData('spartition_1', '3')

    subsets = spart.getSpartitionSubsets('spartition_2')
    assert len(subsets) == 2
    assert '1' in subsets
    assert '2' in subsets
    assert not spart.getSubsetData('spartition_2', '1')
    assert not spart.getSubsetData('spartition_2', '2')

    subsets = spart.getSpartitionSubsets('spartition_3')
    assert len(subsets) == 1
    assert '1' in subsets
    assert not spart.getSubsetData('spartition_3', '1')

    # Validate 'spartition_1'

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '1')
    assert len(subset_individuals) == 1
    assert 'individual_1' in subset_individuals
    assert not spart.getSubsetIndividualData('spartition_1', '1', 'individual_1')

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '2')
    assert len(subset_individuals) == 1
    assert 'individual_2' in subset_individuals
    assert not spart.getSubsetIndividualData('spartition_1', '2', 'individual_2')

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '3')
    assert len(subset_individuals) == 1
    assert 'individual_3' in subset_individuals
    assert not spart.getSubsetIndividualData('spartition_1', '3', 'individual_3')

    # Validate 'spartition_2'

    subset_individuals = spart.getSubsetIndividuals('spartition_2', '1')
    assert len(subset_individuals) == 2
    assert 'individual_1' in subset_individuals
    assert 'individual_2' in subset_individuals
    assert not spart.getSubsetIndividualData('spartition_2', '1', 'individual_1')
    assert not spart.getSubsetIndividualData('spartition_2', '1', 'individual_2')

    subset_individuals = spart.getSubsetIndividuals('spartition_2', '2')
    assert len(subset_individuals) == 1
    assert 'individual_3' in subset_individuals
    assert not spart.getSubsetIndividualData('spartition_2', '2', 'individual_3')

    # Validate 'spartition_3'

    subset_individuals = spart.getSubsetIndividuals('spartition_3', '1')
    assert len(subset_individuals) == 3
    assert 'individual_1' in subset_individuals
    assert 'individual_2' in subset_individuals
    assert 'individual_3' in subset_individuals
    assert not spart.getSubsetIndividualData('spartition_3', '1', 'individual_1')
    assert not spart.getSubsetIndividualData('spartition_3', '1', 'individual_2')
    assert not spart.getSubsetIndividualData('spartition_3', '1', 'individual_3')

def spart_tagged(spart: Spart):
    assert spart.project_name == 'tagged_test'
    assert spart.date == datetime.datetime(2022, 10, 2, 12, 0, 0)

    # Validate individual list

    individuals = spart.getIndividuals()
    assert len(individuals) == 3
    assert 'individual_1' in individuals
    assert 'individual_2' in individuals
    assert 'individual_3' in individuals
    assert spart.getIndividualData('individual_1')['locality'] == 'A'
    assert spart.getIndividualData('individual_2')['locality'] == 'B'
    assert spart.getIndividualData('individual_3')['locality'] == 'C'
    assert spart.getIndividualData('individual_1')['voucher'] == 'X'

    # Validate spartition list

    spartitions = spart.getSpartitions()
    assert len(spartitions) == 3
    assert 'spartition_1' in spartitions
    assert 'spartition_2' in spartitions
    assert 'spartition_3' in spartitions
    assert spart.getSpartitionData('spartition_1')['source'] == 'M'
    assert spart.getSpartitionData('spartition_2')['source'] == 'N'
    assert spart.getSpartitionData('spartition_3')['source'] == 'O'

    # Validate subset lists

    subsets = spart.getSpartitionSubsets('spartition_1')
    assert len(subsets) == 3
    assert '1' in subsets
    assert '2' in subsets
    assert '3' in subsets
    assert spart.getSubsetData('spartition_1', '1')['taxon'] == 'taxon_1_1'
    assert spart.getSubsetData('spartition_1', '2')['taxon'] == 'taxon_1_2'
    assert spart.getSubsetData('spartition_1', '3')['taxon'] == 'taxon_1_3'

    subsets = spart.getSpartitionSubsets('spartition_2')
    assert len(subsets) == 2
    assert '1' in subsets
    assert '2' in subsets
    assert spart.getSubsetData('spartition_2', '1')['taxon'] == 'taxon_2_1'
    assert spart.getSubsetData('spartition_2', '2')['taxon'] == 'taxon_2_2'

    subsets = spart.getSpartitionSubsets('spartition_3')
    assert len(subsets) == 1
    assert '1' in subsets
    assert spart.getSubsetData('spartition_3', '1')['taxon'] == 'taxon_3_1'

    # Validate 'spartition_1'

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '1')
    assert len(subset_individuals) == 1
    assert 'individual_1' in subset_individuals
    assert spart.getSubsetIndividualData('spartition_1', '1', 'individual_1')['score'] == 1.1

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '2')
    assert len(subset_individuals) == 1
    assert 'individual_2' in subset_individuals
    assert spart.getSubsetIndividualData('spartition_1', '2', 'individual_2')['score'] == 1.2

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '3')
    assert len(subset_individuals) == 1
    assert 'individual_3' in subset_individuals
    assert spart.getSubsetIndividualData('spartition_1', '3', 'individual_3')['score'] == 1.3

    # Validate 'spartition_2'

    subset_individuals = spart.getSubsetIndividuals('spartition_2', '1')
    assert len(subset_individuals) == 2
    assert 'individual_1' in subset_individuals
    assert 'individual_2' in subset_individuals
    assert spart.getSubsetIndividualData('spartition_2', '1', 'individual_1')['score'] == 2.1
    assert spart.getSubsetIndividualData('spartition_2', '1', 'individual_2')['score'] == 2.2

    subset_individuals = spart.getSubsetIndividuals('spartition_2', '2')
    assert len(subset_individuals) == 1
    assert 'individual_3' in subset_individuals
    assert spart.getSubsetIndividualData('spartition_2', '2', 'individual_3')['score'] == 2.3

    # Validate 'spartition_3'

    subset_individuals = spart.getSubsetIndividuals('spartition_3', '1')
    assert len(subset_individuals) == 3
    assert 'individual_1' in subset_individuals
    assert 'individual_2' in subset_individuals
    assert 'individual_3' in subset_individuals
    assert spart.getSubsetIndividualData('spartition_3', '1', 'individual_1')['score'] == 3.1
    assert spart.getSubsetIndividualData('spartition_3', '1', 'individual_2')['score'] == 3.2
    assert spart.getSubsetIndividualData('spartition_3', '1', 'individual_3')['score'] == 3.3

def spart_scores(spart: Spart):
    assert spart.project_name == 'scores_test'
    assert spart.date == datetime.datetime(2022, 10, 2, 12, 0, 0)

    # Validate individual list

    individuals = spart.getIndividuals()
    assert len(individuals) == 3
    assert 'individual_1' in individuals
    assert 'individual_2' in individuals
    assert 'individual_3' in individuals
    assert not spart.getIndividualData('individual_1')
    assert not spart.getIndividualData('individual_2')
    assert not spart.getIndividualData('individual_3')

    # Validate spartition list

    spartitions = spart.getSpartitions()
    assert len(spartitions) == 3
    assert 'spartition_1' in spartitions
    assert 'spartition_2' in spartitions
    assert 'spartition_3' in spartitions
    assert spart.getSpartitionScore('spartition_1') == 0.1
    assert spart.getSpartitionScore('spartition_2') == 0.2
    assert spart.getSpartitionScore('spartition_3') == None

    # Validate subset lists

    subsets = spart.getSpartitionSubsets('spartition_1')
    assert len(subsets) == 3
    assert '1' in subsets
    assert '2' in subsets
    assert '3' in subsets
    assert spart.getSubsetScore('spartition_1', '1') == 1.1
    assert spart.getSubsetScore('spartition_1', '2') == 1.2
    assert spart.getSubsetScore('spartition_1', '3') == None

    subsets = spart.getSpartitionSubsets('spartition_2')
    assert len(subsets) == 2
    assert '1' in subsets
    assert '2' in subsets
    assert spart.getSubsetScore('spartition_2', '1') == 2.1
    assert spart.getSubsetScore('spartition_2', '2') == 2.2

    subsets = spart.getSpartitionSubsets('spartition_3')
    assert len(subsets) == 1
    assert '1' in subsets
    assert spart.getSubsetScore('spartition_3', '1') == 3.1

    # Validate 'spartition_1'

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '1')
    assert len(subset_individuals) == 1
    assert 'individual_1' in subset_individuals
    assert spart.getSubsetIndividualScore('spartition_1', '1', 'individual_1') == 1.1

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '2')
    assert len(subset_individuals) == 1
    assert 'individual_2' in subset_individuals
    assert spart.getSubsetIndividualScore('spartition_1', '2', 'individual_2') == 2.1

    subset_individuals = spart.getSubsetIndividuals('spartition_1', '3')
    assert len(subset_individuals) == 1
    assert 'individual_3' in subset_individuals
    assert spart.getSubsetIndividualScore('spartition_1', '3', 'individual_3') == 3.1

    # Validate 'spartition_2'

    subset_individuals = spart.getSubsetIndividuals('spartition_2', '1')
    assert len(subset_individuals) == 2
    assert 'individual_1' in subset_individuals
    assert 'individual_2' in subset_individuals
    assert spart.getSubsetIndividualScore('spartition_2', '1', 'individual_1') == 1.2
    assert spart.getSubsetIndividualScore('spartition_2', '1', 'individual_2') == 2.2

    subset_individuals = spart.getSubsetIndividuals('spartition_2', '2')
    assert len(subset_individuals) == 1
    assert 'individual_3' in subset_individuals
    assert spart.getSubsetIndividualScore('spartition_2', '2', 'individual_3') == 3.2

    # Validate 'spartition_3'

    subset_individuals = spart.getSubsetIndividuals('spartition_3', '1')
    assert len(subset_individuals) == 3
    assert 'individual_1' in subset_individuals
    assert 'individual_2' in subset_individuals
    assert 'individual_3' in subset_individuals
    assert spart.getSubsetIndividualScore('spartition_3', '1', 'individual_1') == None
    assert spart.getSubsetIndividualScore('spartition_3', '1', 'individual_2') == 2.3
    assert spart.getSubsetIndividualScore('spartition_3', '1', 'individual_3') == 3.3

def spart_scores_type(spart: Spart):

    spartitions = spart.getSpartitions()
    assert len(spartitions) == 3
    assert 'spartition_1' in spartitions
    assert 'spartition_2' in spartitions
    assert 'spartition_3' in spartitions
    assert spart.getSubsetScoreType('spartition_1') == 'subset_score_1'
    assert spart.getSpartitionScoreType('spartition_1') == 'spartition_score_1'
    assert spart.getSubsetIndividualScoreType('spartition_1') == 'individual_score_1'

    assert spart.getSubsetScoreType('spartition_2') == 'subset_score_2'
    assert spart.getSpartitionScoreType('spartition_2') == 'spartition_score_2'
    assert spart.getSubsetIndividualScoreType('spartition_2') == 'individual_score_2'

    assert spart.getSubsetScoreType('spartition_3') == None
    assert spart.getSpartitionScoreType('spartition_3') == None
    assert spart.getSubsetIndividualScoreType('spartition_3') == None


test_data = [
    ReadTest('simple.xml', Spart.fromXML, spart_simple),
    ReadTest('simple.spart', Spart.fromMatricial, spart_simple),
    ReadTest('tagged.xml', Spart.fromXML, spart_tagged),
    ReadTest('scores.spart', Spart.fromMatricial, spart_scores),
    ReadTest('scores.xml', Spart.fromXML, spart_scores),
    ReadTest('scores_type.spart', Spart.fromMatricial, spart_scores_type),
    ReadTest('scores_type.xml', Spart.fromXML, spart_scores_type),
    ]


@pytest.mark.parametrize("test", test_data)
def test_read(test: ReadTest) -> None:
    input_path = TEST_DATA_DIR / test.input
    spart = test.reader(input_path)
    test.validator(spart)
