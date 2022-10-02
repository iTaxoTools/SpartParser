
from pathlib import Path
import re

def assert_eq_files(file1: Path, file2: Path) -> None:
    regex = re.compile(r'[\s]')
    text1 = file1.read_text()
    text2 = file2.read_text()
    text1 = regex.sub('', text1)
    text2 = regex.sub('', text2)
    assert text1 == text2
