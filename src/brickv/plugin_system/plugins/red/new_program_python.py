# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_python.py: New Program Wizard Python Page

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

from PyQt4.QtGui import QWizardPage
from brickv.plugin_system.plugins.red.new_program_constants import Constants
from brickv.plugin_system.plugins.red.ui_new_program_python import Ui_NewProgramPython

class NewProgramPython(QWizardPage, Ui_NewProgramPython):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Python Configuration')

        self.registerField('python.version', self.combo_version, 'currentText')
        self.registerField('python.start_mode', self.combo_start_mode)
        self.registerField('python.script', self.edit_script)
        self.registerField('python.module', self.edit_module)
        self.registerField('python.command', self.edit_command)

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify how the new Python program [{0}] should be executed.'
                         .format(str(self.field('name').toString())))
        self.combo_start_mode.setCurrentIndex(0)
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_STDIO

    def update_ui_state(self):
        start_mode = self.field('python.start_mode').toInt()[0]
        start_mode_script = start_mode == Constants.PYTHON_START_MODE_SCRIPT
        start_mode_module = start_mode == Constants.PYTHON_START_MODE_MODULE
        start_mode_command = start_mode == Constants.PYTHON_START_MODE_COMMAND

        self.label_script.setVisible(start_mode_script)
        self.edit_script.setVisible(start_mode_script)
        self.label_module.setVisible(start_mode_module)
        self.edit_module.setVisible(start_mode_module)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
