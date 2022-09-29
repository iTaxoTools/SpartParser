"""The setup module for SpartParser"""

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="spart_parser",
    version="0.0.1",
    description="Parse and write SPART files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iTaxoTools/concatenator/",
    author="Khushil Prajapati",
    package_dir={"": "src"},
    packages=find_namespace_packages(
        include=("itaxotools*",),
        where="src",
    ),
    python_requires=">=3.8.6, <4",
    install_requires=[
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
        ],
        "gui": [
            "PySide6>=6.3.2",
            "itaxotools-common==0.2.dev3",
        ],
    },
    entry_points={
        "console_scripts": [
            "SpartParser=itaxotools.spart_parser.main:main",
            "SpartParserDemo=itaxotools.spart_parser.main:demo",
            "SpartParserGui=itaxotools.spart_parser.gui:run",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    include_package_data=True,
)
