# -----------------------------------------------------------------------------
# Taxi3Gui - GUI for Taxi3
# Copyright (C) 2022  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------


from enum import Enum
from pathlib import Path
from shutil import copy
from tempfile import TemporaryDirectory

from itaxotools.spart_parser import Spart

from .utility import Property, PropertyObject


class SpartType(Enum):
    Matricial = "Matricial Spart", ".spart"
    XML = "Spart-XML", ".xml"

    def __init__(self, description, extension):
        self.description = description
        self.extension = extension

    def __str__(self):
        return self.description


class AppModel(PropertyObject):
    path_input = Property(Path)
    path_matricial = Property(Path)
    path_xml = Property(Path)
    work_dir = Property(Path)
    input_name = Property(str)
    individuals = Property(object)
    spartitions = Property(object)
    status = Property(str)
    ready = Property(bool)
    spart = Property(Spart)

    def __init__(self):
        super().__init__()
        self.temp_dir = TemporaryDirectory(prefix="spart_")
        self.temp_path = Path(self.temp_dir.name)
        self.object = None
        self.ready = False
        self.work_dir = None
        self.input_name = None
        self.individuals = None
        self.spartitions = None
        self.status = "Open a file to begin."

    def open(self, path: Path):
        parsed_matricial = self.temp_path / f"{path.name}.parsed.spart"
        parsed_xml = self.temp_path / f"{path.name}.parsed.xml"

        try:
            spart = Spart.fromPath(path)
            spart.toMatricial(parsed_matricial)
            spart.toXML(parsed_xml)
        except Exception as e:
            raise Exception(f"Could not open file: {path.name}") from e

        self.work_dir = path.parent
        self.path_input = path
        self.path_matricial = parsed_matricial
        self.path_xml = parsed_xml
        self.input_name = path.name

        self.individuals = len(spart.getIndividuals())
        self.spartitions = len(spart.getSpartitions())

        self.spart = spart
        self.ready = True
        self.status = f"Successfully opened file: {self.shorten(self.input_name)}"

    def save(self, destination: Path, type: SpartType):
        source = {
            SpartType.Matricial: self.path_matricial,
            SpartType.XML: self.path_xml,
        }[type]
        copy(source, destination)
        self.status = (
            f"Successfully saved {str(type)} file: {self.shorten(destination.name)}"
        )

    def shorten(self, name):
        if len(name) < 30:
            return name
        return f"{name[:15]}...{name[-15:]}"
