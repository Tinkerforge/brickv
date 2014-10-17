# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program.py: New Program Wizard

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWizard
from brickv.plugin_system.plugins.red.new_program_pages import *
from brickv.plugin_system.plugins.red.new_program_general import NewProgramGeneral
from brickv.plugin_system.plugins.red.new_program_files import NewProgramFiles
from brickv.plugin_system.plugins.red.new_program_java import NewProgramJava
from brickv.plugin_system.plugins.red.new_program_python import NewProgramPython

class NewProgram(QWizard):
    def __init__(self, identifiers, *args, **kwargs):
        QWizard.__init__(self, *args, **kwargs)

        self.identifiers = identifiers

        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        self.setWindowTitle('New Program')

        self.setPage(PAGE_GENERAL, NewProgramGeneral())
        self.setPage(PAGE_FILES, NewProgramFiles())
        self.setPage(PAGE_JAVA, NewProgramJava())
        self.setPage(PAGE_PYTHON, NewProgramPython())

    # overrides QWizard.sizeHint
    def sizeHint(self):
        size = QWizard.sizeHint(self)

        if size.height() < 550:
            size.setHeight(550)

        return size
