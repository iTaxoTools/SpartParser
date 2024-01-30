from pathlib import Path

from pytest import mark

from itaxotools.spart_parser.gui.main import Main

TEST_DATA_DIR = Path(__file__).parent / "data"


test_filenames = [
    "simple.spart",
    "simple.xml",
]


@mark.parametrize("filename", test_filenames)
def test_main(qapp, filename):
    path = TEST_DATA_DIR / filename
    Main(files=[path])
