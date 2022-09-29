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

"""Main dialog window"""

from PySide6 import QtCore, QtGui, QtWidgets

import shutil
from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.common.widgets import ToolDialog, ScalingImage, VLineSeparator

from . import app
from .utility import bind, unbind
from .model import SpartType


class ToolLogo(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFixedWidth(320)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setPixmap(app.resources.pixmaps.logo_tool)


class ProjectLogo(ScalingImage):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setFixedHeight(64)
        self.logo = app.resources.pixmaps.logo_project


class ToolBar(QtWidgets.QToolBar):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum)
        self.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.setStyleSheet("""
            QToolBar {
                spacing: 2px;
                }
            QToolButton {
                color: palette(Shadow);
                background: transparent;
                border: 1px solid transparent;
                border-radius: 2px;
                letter-spacing: 1px;
                font-weight: bold;
                font-size: 14px;
                min-width: 74px;
                min-height: 38px;
                padding: 0px 8px 0px 8px;
                margin: 0px 0px 0px 0px;
                text-align: right;
                }
            QToolButton:disabled {
                color: palette(Dark);
                }
            QToolButton:hover {
                background: palette(Window);
                border: 1px solid transparent;
                }
            QToolButton:pressed {
                background: palette(Midlight);
                border: 1px solid palette(Mid);
                border-radius: 2px;
                }
            QToolButton[popupMode="2"]:pressed {
                padding-bottom: 5px;
                border: 1px solid palette(Dark);
                margin: 5px 1px 0px 1px;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                }
            QToolButton::menu-indicator {
                image: none;
                width: 30px;
                border-bottom: 1px solid palette(Mid);
                subcontrol-origin: padding;
                subcontrol-position: bottom;
                }
            QToolButton::menu-indicator:disabled {
                border-bottom: 1px solid palette(Midlight);
                }
            QToolButton::menu-indicator:pressed {
                border-bottom: 0px;
                }
            """)


class Header(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw()

    def draw(self):
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum)
        self.setStyleSheet("""
            Header {
                background: palette(Light);
                border-top: 1px solid palette(Mid);
                border-bottom: 1px solid palette(Dark);
                }
            """)
        self.toolLogo = ToolLogo(self)
        self.projectLogo = ProjectLogo(self)
        self.toolBar = ToolBar(self)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.toolLogo)
        layout.addWidget(VLineSeparator(1))
        layout.addSpacing(4)
        layout.addWidget(self.toolBar)
        layout.addSpacing(8)
        layout.addStretch(8)
        layout.addWidget(self.projectLogo)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class TextView(QtWidgets.QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.document().setDocumentMargin(8)
        self.setAcceptRichText(False)
        self.setReadOnly(True)
        # self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    def open(self, path: Path):
        if path is None:
            self.clear()
            return
        with open(path) as file:
            text = file.read()
            self.setText(text)


class Body(QtWidgets.QSplitter):
    def __init__(self, *args, **kwargs):
        super().__init__(QtCore.Qt.Horizontal)

        self.left_panel = TextView('LEFT')
        self.right_panel = TextView('RIGHT')

        self.addWidget(self.left_panel)
        self.addWidget(self.right_panel)
        self.setStretchFactor(0, 1)
        self.setStretchFactor(1, 1)
        self.setCollapsible(0, False)
        self.setCollapsible(1, False)
        self.setStyleSheet("QSplitter::handle { height: 12px; }")
        self.setContentsMargins(32, 24, 32, 24)

        bind(app.model.properties.path_matricial, self.left_panel.open)
        bind(app.model.properties.path_xml, self.right_panel.open)


class InfoLabel(QtWidgets.QLabel):
    def __init__(self, text, value=None):
        super().__init__()
        self.prefix = text
        self.setValue(value)

    def setValue(self, value=None):
        if value is None:
            value = '-'
        self.value = value
        if isinstance(value, int):
            value = f'{value:,}'
        self.setText(f'{self.prefix}: {value}')


class Footer(QtWidgets.QFrame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedHeight(32)
        self.setStyleSheet("""
            Footer {
                color: palette(Shadow);
                background: palette(Window);
                border: 0px solid transparent;
                border-top: 1px solid palette(Dark);
                padding: 5px 10px 5px 10px;
                }
            Footer:disabled {
                color: palette(Mid);
                background: palette(Window);
                border: 1px solid palette(Mid);
                }
            """)

        self.status = QtWidgets.QLabel('STATUS')
        self.individuals = InfoLabel('Individuals')
        self.spartitions = InfoLabel('Spartitions')

        bind(app.model.properties.individuals, self.individuals.setValue)
        bind(app.model.properties.spartitions, self.spartitions.setValue)
        bind(app.model.properties.status, self.status.setText)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.status)
        layout.addStretch(1)
        layout.addWidget(self.individuals)
        layout.addSpacing(8)
        layout.addWidget(self.spartitions)
        layout.setContentsMargins(8, 0, 8, 0)
        self.setLayout(layout)


class Main(ToolDialog):
    """Main window, handles everything"""

    def __init__(self, parent=None, files=[]):
        super(Main, self).__init__(parent)

        self.title = 'SpartParser'

        self.setWindowIcon(app.resources.icons.app)
        self.setWindowTitle(self.title)
        self.resize(800, 500)

        self.draw()
        self.act()

        bind(app.model.properties.input_name, self.setWindowTitle,
            lambda x: self.title if not x else f'{self.title} - {x}')

    def draw(self):
        """Draw all contents"""
        self.widgets = AttrDict()
        self.widgets.header = Header(self)
        self.widgets.sidebar = QtWidgets.QWidget(self)
        self.widgets.body = Body(self)
        self.widgets.footer = Footer(self)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.widgets.header, 0, 0, 1, 2)
        layout.addWidget(self.widgets.sidebar, 1, 0, 1, 1)
        layout.addWidget(self.widgets.body, 1, 1, 1, 1)
        layout.addWidget(self.widgets.footer, 2, 0, 1, 2)
        layout.setSpacing(0)
        layout.setColumnStretch(1, 1)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def act(self):
        """Populate dialog actions"""
        self.actions = {}

        self.actions['open'] = QtGui.QAction('&Open', self)
        self.actions['open'].setIcon(app.resources.icons.open)
        self.actions['open'].setShortcut(QtGui.QKeySequence.Open)
        self.actions['open'].setStatusTip('Open an existing file')
        self.actions['open'].triggered.connect(self.handleOpen)

        self.actions['save_matricial'] = QtGui.QAction('&Matricial', self)
        self.actions['save_matricial'].setIcon(app.resources.icons.save)
        self.actions['save_matricial'].setStatusTip('Save Matricial')
        self.actions['save_matricial'].triggered.connect(self.handleSaveMatricial)

        self.actions['save_xml'] = QtGui.QAction('&XML', self)
        self.actions['save_xml'].setIcon(app.resources.icons.save)
        self.actions['save_xml'].setStatusTip('Save XML')
        self.actions['save_xml'].triggered.connect(self.handleSaveXML)

        self.widgets.header.toolBar.addAction(self.actions['open'])
        self.widgets.header.toolBar.addAction(self.actions['save_matricial'])
        self.widgets.header.toolBar.addAction(self.actions['save_xml'])

        bind(app.model.properties.ready, self.actions['save_matricial'].setEnabled)
        bind(app.model.properties.ready, self.actions['save_xml'].setEnabled)

    def handleHome(self):
        self.widgets.body.showDashboard()

    def handleOpen(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, f'{self.title} - Open File')
        if not filename:
            return
        QtCore.QDir.setCurrent(str(Path(filename).parent))
        app.model.open(Path(filename))

    def handleSave(self, type):
        suggested_name = app.model.path_input.stem + type.extension
        destination = Path(app.model.work_dir / suggested_name)
        filters = f'{type.description} (*{type.extension})'
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, f'{self.title} - Save File',
            str(destination), filters)
        if not filename:
            return
        app.model.save(Path(filename), type)

    def handleSaveMatricial(self):
        self.handleSave(SpartType.Matricial)

    def handleSaveXML(self):
        self.handleSave(SpartType.XML)
