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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWizardPage, QListWidgetItem
from brickv.plugin_system.plugins.red.new_program_constants import Constants
from brickv.plugin_system.plugins.red.ui_new_program_java import Ui_NewProgramJava

class NewProgramJava(QWizardPage, Ui_NewProgramJava):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Java Configuration')

        self.registerField('java.version', self.combo_version)
        self.registerField('java.start_mode', self.combo_start_mode)
        self.registerField('java.main_class', self.edit_main_class)
        self.registerField('java.jar_file', self.edit_jar_file)

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.list_arguments.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_argument.clicked.connect(self.add_argument)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify how the new Java program [{0}] should be executed.'
                         .format(str(self.field('name').toString())))
        self.combo_start_mode.setCurrentIndex(0)
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_STDIO

    def update_ui_state(self):
        start_mode = self.field('java.start_mode').toInt()[0]
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file = start_mode == Constants.JAVA_START_MODE_JAR_FILE

        self.label_main_class.setVisible(start_mode_main_class)
        self.edit_main_class.setVisible(start_mode_main_class)
        self.label_main_class_help.setVisible(start_mode_main_class)
        self.label_jar_file.setVisible(start_mode_jar_file)
        self.edit_jar_file.setVisible(start_mode_jar_file)
        self.label_jar_file_help.setVisible(start_mode_jar_file)

        has_selection = len(self.list_arguments.selectedItems()) > 0

        self.button_up_argument.setEnabled(has_selection)
        self.button_down_argument.setEnabled(has_selection)
        self.button_remove_argument.setEnabled(has_selection)

    def add_argument(self):
        argument = QListWidgetItem('<new argument>')
        argument.setFlags(argument.flags() | Qt.ItemIsEditable);

        self.list_arguments.addItem(argument)
        self.list_arguments.editItem(argument)
