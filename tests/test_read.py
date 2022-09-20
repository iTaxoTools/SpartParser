import pytest
from json import dumps
from pathlib import Path

from itaxotools.spart_parser import SpartParser, SpartParserRegular

TEST_DATA_DIR = Path(__file__).parent.parent / 'examples'


test_files = list(TEST_DATA_DIR.iterdir())


@pytest.mark.parametrize("path", test_files)
def test_read_sanity(path: Path):
    if path.suffix == '.xml':
        spartParser = SpartParser(str(path))
    else:
        spartParser = SpartParserRegular(str(path))
    x = spartParser.generateData()
    print(dumps(x))
