# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_java.py: New Program Wizard Java Page

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
from brickv.plugin_system.plugins.red.ui_new_program_java import Ui_NewProgramJava

class NewProgramJava(QWizardPage, Ui_NewProgramJava):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Java Configuration')

        self.registerField('java.version', self.combo_version, 'currentText')
        self.registerField('java.mode', self.combo_mode, 'currentText')
        self.registerField('java.class', self.edit_class)
        self.registerField('java.jar', self.edit_jar)

        self.combo_mode.currentIndexChanged.connect(self.update_ui_state)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify how the new Java program [{0}] should be executed.'.format(str(self.field('identifier').toString())))
        self.combo_mode.setCurrentIndex(0)
        self.update_ui_state()

    def update_ui_state(self):
        mode = str(self.field('java.mode').toString())

        self.label_class.setEnabled(mode == 'Class')
        self.edit_class.setEnabled(mode == 'Class')
        self.label_jar.setEnabled(mode == 'JAR')
        self.edit_jar.setEnabled(mode == 'JAR')
