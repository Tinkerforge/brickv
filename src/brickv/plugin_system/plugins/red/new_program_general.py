# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_general.py: New Program Wizard General Page

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

from PyQt4.QtCore import QRegExp, QString, Qt
from PyQt4.QtGui import QWizardPage, QRegExpValidator, QMessageBox
from brickv.plugin_system.plugins.red.new_program_utils import *
from brickv.plugin_system.plugins.red.ui_new_program_general import Ui_NewProgramGeneral
import re

class NewProgramGeneral(QWizardPage, Ui_NewProgramGeneral):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.identifier_is_unique = False

        self.setTitle('Step 1 of {0}: General Information'.format(Constants.STEP_COUNT))
        self.setSubTitle('Specify name, identifier and programming language for the new program.')

        self.edit_identifier.setValidator(QRegExpValidator(QRegExp('^[a-zA-Z0-9_][a-zA-Z0-9._-]{2,}$'), self))

        self.registerField('name', self.edit_name)
        self.registerField('identifier', self.edit_identifier)
        self.registerField('language', self.combo_language)

        self.edit_name.textChanged.connect(self.auto_generate_identifier)
        self.check_auto_generate.stateChanged.connect(self.update_ui_state)
        self.edit_identifier.textChanged.connect(self.check_identifier)
        self.combo_language.currentIndexChanged.connect(self.check_language)

        self.edit_name_checker = MandatoryLineEditChecker(self, self.edit_name, self.label_name)
        self.edit_identifier_checker = MandatoryLineEditChecker(self, self.edit_identifier, self.label_identifier)

        self.check_language(self.combo_language.currentIndex())

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.edit_name.setText('unnamed')
        self.combo_language.setCurrentIndex(Constants.LANGUAGE_INVALID)
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_FILES

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.edit_name_checker.valid and \
               self.edit_identifier_checker.valid and \
               self.identifier_is_unique and \
               self.field('language').toInt()[0] != Constants.LANGUAGE_INVALID and \
               QWizardPage.isComplete(self)

    def update_ui_state(self):
        auto_generate = self.check_auto_generate.checkState() == Qt.Checked

        self.auto_generate_identifier(self.edit_name.text())

        self.label_identifier.setVisible(not auto_generate)
        self.edit_identifier.setVisible(not auto_generate)
        self.label_identifier_help.setVisible(not auto_generate)

    def auto_generate_identifier(self, name):
        if self.check_auto_generate.checkState() != Qt.Checked:
            return

        name = unicode(name) # convert QString to Unicode

        # ensure the identifier matches ^[a-zA-Z0-9_][a-zA-Z0-9._-]{2,}$
        identifier = str(re.sub('[^a-zA-Z0-9._-]', '_', name)).lstrip('-.')

        while len(identifier) < 3:
            identifier += '_'

        unique_identifier = identifier
        counter = 1

        while unique_identifier in self.wizard().identifiers and counter < 10000:
            unique_identifier = identifier + str(counter)
            counter += 1

        self.edit_identifier.setText(unique_identifier)

        if unique_identifier in self.wizard().identifiers:
            QMessageBox.critical(self, 'Identifier Error',
                                 u'Could not auto-generate unique identifier from program name [{0}] because all tested ones are already in use.'
                                 .format(name))

    def check_identifier(self, identifier):
        identifier = str(identifier) # convert QString to ASCII
        identifier_was_unique = self.identifier_is_unique

        if identifier in self.wizard().identifiers:
            self.identifier_is_unique = False
            self.edit_identifier.setStyleSheet('QLineEdit { color : red }')
        else:
            self.identifier_is_unique = True
            self.edit_identifier.setStyleSheet('')

        if identifier_was_unique != self.identifier_is_unique:
            self.completeChanged.emit()

    def check_language(self, language):
        if language == Constants.LANGUAGE_INVALID:
            self.label_language.setStyleSheet('QLabel { color : red }')
        else:
            self.label_language.setStyleSheet('')

        self.completeChanged.emit()
