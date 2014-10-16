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
from brickv.plugin_system.plugins.red.ui_new_program_python import Ui_NewProgramPython

class NewProgramPython(QWizardPage, Ui_NewProgramPython):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Python Configuration')

        self.registerField('python.version', self.combo_version, 'currentText')
        self.registerField('python.mode', self.combo_mode, 'currentText')
        self.registerField('python.script', self.edit_script)
        self.registerField('python.module', self.edit_module)
        self.registerField('python.command', self.edit_command)

        self.combo_mode.currentIndexChanged.connect(self.update_ui_state)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify how the new Python program [{0}] should be executed.'.format(str(self.field('identifier').toString())))
        self.combo_mode.setCurrentIndex(0)
        self.update_ui_state()

    def update_ui_state(self):
        mode = str(self.field('python.mode').toString())

        self.label_script.setEnabled(mode == 'Script')
        self.edit_script.setEnabled(mode == 'Script')
        self.label_module.setEnabled(mode == 'Module')
        self.edit_module.setEnabled(mode == 'Module')
        self.label_command.setEnabled(mode == 'Command')
        self.edit_command.setEnabled(mode == 'Command')
