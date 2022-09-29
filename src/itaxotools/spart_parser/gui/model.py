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


from PySide6 import QtCore

from pathlib import Path
from tempfile import TemporaryDirectory
from enum import Enum, auto
from shutil import copy

from .utility import Property, PropertyObject


class SpartType(Enum):
    Matricial = 'Matricial Spart', '.spart'
    XML = 'Spart-XML', '.xml'

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
    input_type = Property(SpartType)
    individuals = Property(object)
    spartitions = Property(object)
    status = Property(str)
    ready = Property(bool)
    object = Property(object)

    def __init__(self):
        super().__init__()
        self.temp_dir = TemporaryDirectory(prefix='spart_')
        self.temp_path = Path(self.temp_dir.name)
        self.object = None
        self.ready = False
        self.work_dir = None
        self.input_name = None
        self.input_type = None
        self.individuals = None
        self.spartitions = None
        self.status = 'Open a file to begin.'

    def open(self, path: Path):
        converted_path = self.temp_path / f'{path.name}.xml'
        copy(path, converted_path)

        self.work_dir = path.parent
        self.path_input = path
        self.path_matricial = path
        self.path_xml = converted_path
        self.input_name = path.name

        self.object = None
        self.individuals = 41
        self.spartitions = 43
        self.input_type = SpartType.Matricial

        self.ready = True
        print(f'OPEN: {str(path)} > {str(converted_path)}')
        self.status = f'Successfully opened {str(self.input_type)} file: {self.shorten(self.input_name)}'

    def save(self, destination: Path, type: SpartType):
        source = {
            SpartType.Matricial: self.path_matricial,
            SpartType.XML: self.path_xml,
        }[type]
        print(f'COPY: {str(source)} > {str(destination)}')
        self.status = f'Successfully saved {str(type)} file: {self.shorten(destination.name)}'

    def shorten(self, name):
        if len(name) < 30:
            return name
        return f'{name[:15]}...{name[-15:]}'
