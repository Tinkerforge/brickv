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
from brickv.plugin_system.plugins.red.new_program_utils import Constants, MandatoryLineEditChecker
from brickv.plugin_system.plugins.red.ui_new_program_java import Ui_NewProgramJava

class NewProgramJava(QWizardPage, Ui_NewProgramJava):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Step 3 of {0}: Java Configuration'.format(Constants.STEP_COUNT))

        self.registerField('java.version', self.combo_version)
        self.registerField('java.start_mode', self.combo_start_mode)
        self.registerField('java.main_class', self.edit_main_class)
        self.registerField('java.jar_file', self.combo_jar_file, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.emit_complete_changed)
        self.edit_main_class.textChanged.connect(self.emit_complete_changed)
        self.combo_jar_file.currentIndexChanged.connect(self.emit_complete_changed)
        self.combo_jar_file.editTextChanged.connect(self.emit_complete_changed)

        self.edit_main_class_checker = MandatoryLineEditChecker(self.edit_main_class, self.label_main_class)
        self.combo_jar_file_checker = MandatoryLineEditChecker(self.combo_jar_file.lineEdit(), self.label_jar_file)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Specify how the new Java program [{0}] should be executed.'
                         .format(unicode(self.field('name').toString())))
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_JAVA_START_MODE)
        self.combo_jar_file.clear()

        for upload in self.wizard().page(Constants.PAGE_FILES).get_uploads():
            if upload.target.lower().endswith('.jar'):
                self.combo_jar_file.addItem(upload.target)

        if self.combo_jar_file.count() > 1:
            self.combo_jar_file.clearEditText()

        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_ARGUMENTS

    # overrides QWizardPage.isComplete
    def isComplete(self):
        start_mode = self.field('java.start_mode').toInt()[0]

        if start_mode == Constants.JAVA_START_MODE_MAIN_CLASS and \
           len(self.edit_main_class.text()) == 0:
            return False

        if start_mode == Constants.JAVA_START_MODE_JAR_FILE and \
           len(self.combo_jar_file.currentText()) == 0:
            return False

        return QWizardPage.isComplete(self)

    def update_ui_state(self):
        start_mode = self.field('java.start_mode').toInt()[0]
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file = start_mode == Constants.JAVA_START_MODE_JAR_FILE

        self.label_main_class.setVisible(start_mode_main_class)
        self.edit_main_class.setVisible(start_mode_main_class)
        self.label_main_class_help.setVisible(start_mode_main_class)
        self.label_jar_file.setVisible(start_mode_jar_file)
        self.combo_jar_file.setVisible(start_mode_jar_file)
        self.label_jar_file_help.setVisible(start_mode_jar_file)

    def emit_complete_changed(self):
        self.completeChanged.emit()
