import pytest
from json import dumps
from pathlib import Path

from itaxotools.spart_parser import Spart

TEST_DATA_DIR = Path(__file__).parent.parent / 'examples'


test_files = list(TEST_DATA_DIR.iterdir())


@pytest.mark.parametrize("path", test_files)
def test_examples(path: Path):
    spart = Spart.fromPath(path)
