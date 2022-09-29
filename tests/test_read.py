import pytest
from json import dumps
from pathlib import Path

from itaxotools.spart_parser import SpartParser, SpartParserRegular
from itaxotools.spart_parser.skeleton import SpartDict

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


# def test_read_write(tmp_path: Path):
#     in_path = TEST_DATA_DIR / 'spart.xml'
#     out_path = tmp_path / 'out.xml'
#     spart = SpartDict.read_xml(in_path)
#     spart = SpartDict(spart)
#     spart.write_xml(out_path)
#     assert in_path.read_text() == out_path.read_text()
