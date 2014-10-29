# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Matthias <matthias@tinkerforge.com>

red_tab_program.py: RED program tab implementation

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

from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QWidget, QDialog, QMessageBox, QListWidgetItem
from brickv.plugin_system.plugins.red.ui_red_tab_program import Ui_REDTabProgram
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_info import ProgramInfo
from brickv.plugin_system.plugins.red.program_wizard_new import ProgramWizardNew
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.async_call import async_call

class REDTabProgram(QWidget, Ui_REDTabProgram):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.script_manager = None
        self.session = None
        self.image_version_ref = ['<unknown>']
        self.new_program_wizard = None

        self.splitter.setSizes([200, 400])
        self.list_programs.itemSelectionChanged.connect(self.update_ui_state)
        self.button_refresh.clicked.connect(self.refresh_program_list)
        self.button_new.clicked.connect(self.show_new_program_wizard)
        self.button_delete.clicked.connect(self.purge_selected_program)

        self.update_ui_state()

    def tab_on_focus(self):
        if self.image_version_ref[0] == '<unknown>':
            # FIXME: this is should actually be sync to ensure that the image version is known before it'll be used
            def read_image_version():
                self.image_version_ref[0] = REDFile(self.session).open('/etc/tf_image_version', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0).read(256)

            async_call(read_image_version, None, None, None)

        self.refresh_program_list()

    def tab_off_focus(self):
        pass

    def update_ui_state(self):
        has_selection = len(self.list_programs.selectedItems()) > 0

        if has_selection:
            row = self.list_programs.row(self.list_programs.selectedItems()[0])
            self.stacked_container.setCurrentIndex(row + 1)

        self.button_delete.setEnabled(has_selection)

    def add_program_to_list(self, program):
        program_info = ProgramInfo(self.session, self.script_manager, self.image_version_ref, program)
        program_info.name_changed.connect(self.refresh_program_names)

        item = QListWidgetItem(program.cast_custom_option_value(Constants.FIELD_NAME, unicode, '<unknown>'))
        item.setData(Qt.UserRole, QVariant(program_info))

        self.list_programs.addItem(item)
        self.stacked_container.addWidget(program_info)

    def refresh_program_list(self):
        def refresh_async():
            return get_programs(self.session).items

        def cb_success(programs):
            for program in programs:
                self.add_program_to_list(program)

            self.button_refresh.setText('Refresh')
            self.button_refresh.setEnabled(True)
            self.update_ui_state()
            self.stacked_container.setCurrentIndex(1)

        def cb_error():
            self.button_refresh.setText('Error')

        self.button_refresh.setText('Refreshing...')
        self.button_refresh.setEnabled(False)

        self.list_programs.clear()

        while self.stacked_container.count() > 1:
            self.stacked_container.removeWidget(self.stacked_container.currentWidget())

        async_call(refresh_async, None, cb_success, cb_error)

    def refresh_program_names(self):
        for i in range(self.list_programs.count()):
            item = self.list_programs.item(i)
            program = item.data(Qt.UserRole).toPyObject().program
            item.setText(program.cast_custom_option_value('name', unicode, '<unknown>'))

    def show_new_program_wizard(self):
        self.button_new.setEnabled(False)

        identifiers = []

        for i in range(self.list_programs.count()):
            identifiers.append(str(self.list_programs.item(i).data(Qt.UserRole).toPyObject().program.identifier))

        context = ProgramWizardContext(self.session, identifiers, self.script_manager, self.image_version_ref)

        self.new_program_wizard = ProgramWizardNew(context)
        self.new_program_wizard.finished.connect(self.new_program_wizard_finished)
        self.new_program_wizard.show()

    def new_program_wizard_finished(self, result):
        self.new_program_wizard.finished.disconnect(self.new_program_wizard_finished)

        if result == QDialog.Accepted:
            self.add_program_to_list(self.new_program_wizard.program)
            self.list_programs.item(self.list_programs.count() - 1).setSelected(True)

        self.button_new.setEnabled(True)

    def purge_selected_program(self):
        selected_items = self.list_programs.selectedItems()

        if len(selected_items) == 0:
            return

        program_info = selected_items[0].data(Qt.UserRole).toPyObject()
        program = program_info.program
        name = str(program_info.program.identifier) # FIXME: get program name

        button = QMessageBox.question(self, 'Delete Program',
                                      u'Deleting program [{0}] is irreversible. All files of this program will be deleted.'.format(name),
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if button != QMessageBox.Ok:
            return

        program_info.name_changed.disconnect(self.refresh_program_names)

        try:
            program.purge() # FIXME: async_call
        except REDError as e:
            QMessageBox.critical(self, 'Delete Error',
                                 u'Could not delete program [{0}]:\n\n{1}'.format(name, str(e)))
            return

        QMessageBox.information(self, 'Delete Successful',
                                 u'Program [{0}] successful deleted!'.format(name))

        self.stacked_container.removeWidget(program_info)
        self.list_programs.takeItem(self.list_programs.row(selected_items[0]))
