# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QApplication, QMessageBox, QTreeWidgetItem

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_program import Ui_REDTabProgram
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_info_main import ProgramInfoMain
from brickv.plugin_system.plugins.red.program_wizard import ProgramWizardContext
from brickv.plugin_system.plugins.red.program_wizard_new import ProgramWizardNew
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.program_page_delphi import get_fpc_versions
from brickv.plugin_system.plugins.red.program_page_c import get_gcc_versions
from brickv.plugin_system.plugins.red.program_page_delphi import get_lazbuild_versions
from brickv.plugin_system.plugins.red.program_page_java import get_java_versions
from brickv.plugin_system.plugins.red.program_page_csharp import get_mono_versions
from brickv.plugin_system.plugins.red.program_page_javascript import get_nodejs_versions
from brickv.plugin_system.plugins.red.program_page_octave import get_octave_versions
from brickv.plugin_system.plugins.red.program_page_perl import get_perl_versions
from brickv.plugin_system.plugins.red.program_page_php import get_php_versions
from brickv.plugin_system.plugins.red.program_page_python import get_python_versions
from brickv.plugin_system.plugins.red.program_page_ruby import get_ruby_versions
from brickv.plugin_system.plugins.red.program_page_shell import get_shell_versions
from brickv.async_call import async_call
from brickv.utils import get_main_window

class REDTabProgram(REDTab, Ui_REDTabProgram):
    def __init__(self):
        REDTab.__init__(self)

        self.setupUi(self)

        self.executable_versions = {
            'fpc':    None,
            'gcc':    None,
            'java':   None,
            'mono':   None,
            'nodejs': None,
            'octave': None,
            'perl':   None,
            'php':    None,
            'python': None,
            'ruby':   None,
            'shell':  None
        }
        self.first_tab_on_focus  = True
        self.tab_is_alive        = True
        self.refresh_in_progress = False
        self.new_program_wizard  = None

        self.splitter.setSizes([175, 400])
        self.tree_programs.setColumnWidth(0, 150)
        self.tree_programs.setColumnWidth(1, 50)

        self.tree_programs.itemSelectionChanged.connect(self.update_ui_state)
        self.button_refresh.clicked.connect(self.refresh_program_tree)
        self.button_new.clicked.connect(self.show_new_program_wizard)
        self.button_delete.clicked.connect(self.purge_selected_program)

        self.update_ui_state()

    def tab_on_focus(self):
        if self.first_tab_on_focus:
            self.first_tab_on_focus = False

            QTimer.singleShot(1, self.refresh_program_tree)
            QTimer.singleShot(1, self.refresh_executable_versions)

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        self.tab_is_alive = False

        if self.new_program_wizard != None:
            self.new_program_wizard.close()

        for i in range(self.stacked_container.count()):
            widget = self.stacked_container.widget(i)

            if isinstance(widget, ProgramInfoMain):
                widget.close_all_dialogs()

    def update_ui_state(self):
        if self.refresh_in_progress:
            self.progress_refresh.setVisible(True)
            self.button_refresh.setText('Refreshing...')
            self.button_refresh.setEnabled(False)
            self.button_new.setEnabled(False)
            self.button_delete.setEnabled(False)
        else:
            self.progress_refresh.setVisible(False)
            self.button_refresh.setText('Refresh')
            self.button_refresh.setEnabled(True)
            self.button_new.setEnabled(True)

            has_selection = len(self.tree_programs.selectedItems()) > 0

            if not has_selection and self.tree_programs.topLevelItemCount() > 0:
                self.tree_programs.topLevelItem(0).setSelected(True)
                has_selection = True

            if has_selection:
                index = self.tree_programs.indexOfTopLevelItem(self.tree_programs.selectedItems()[0])
                self.stacked_container.setCurrentIndex(index + 1)

            self.button_delete.setEnabled(has_selection)

    def add_program_to_tree(self, program):
        program_info = ProgramInfoMain(self.session, self.script_manager, self.image_version, self.executable_versions, program)
        program_info.name_changed.connect(self.refresh_program_name)
        program_info.status_changed.connect(self.refresh_program_status)

        item = QTreeWidgetItem([program.cast_custom_option_value('name', unicode, '<unknown>'),
                                get_program_short_status(program)])
        item.setData(0, Qt.UserRole, program_info)

        self.tree_programs.addTopLevelItem(item)
        self.stacked_container.addWidget(program_info)

    def refresh_program_tree(self):
        def refresh_async():
            return get_programs(self.session)

        def cb_success(programs):
            sorted_programs = {}

            for program in programs:
                first_upload = program.cast_custom_option_value('first_upload', int, 0)

                if first_upload in sorted_programs:
                    sorted_programs[first_upload][program.identifier] = program
                else:
                    sorted_programs[first_upload] = {program.identifier: program}

            for first_upload in sorted(sorted_programs.keys()):
                for identifier in sorted(sorted_programs[first_upload].keys()):
                    self.add_program_to_tree(sorted_programs[first_upload][identifier])

            self.refresh_in_progress = False
            self.update_ui_state()
            self.stacked_container.setCurrentIndex(1)

        def cb_error():
            pass # FIXME: report error

        self.refresh_in_progress = True
        self.update_ui_state()
        self.tree_programs.clear()
        QApplication.processEvents()

        # move help widget to front so the other widgets wont show and update during removal
        self.stacked_container.setCurrentWidget(self.widget_help)

        while self.stacked_container.count() > 1:
            self.stacked_container.removeWidget(self.stacked_container.widget(1))
            QApplication.processEvents()

        async_call(refresh_async, None, cb_success, cb_error)

    def refresh_program_name(self, program):
        for i in range(self.tree_programs.topLevelItemCount()):
            item = self.tree_programs.topLevelItem(i)

            if item.data(0, Qt.UserRole).program == program:
                item.setText(0, program.cast_custom_option_value('name', unicode, '<unknown>'))

    def refresh_program_status(self, program):
        for i in range(self.tree_programs.topLevelItemCount()):
            item = self.tree_programs.topLevelItem(i)

            if item.data(0, Qt.UserRole).program == program:
                item.setText(1, get_program_short_status(program))

    def refresh_executable_versions(self):
        def cb_versions(executable_name, versions):
            self.executable_versions[executable_name] = versions

        get_fpc_versions(self.script_manager, lambda versions: cb_versions('fpc', versions))
        get_gcc_versions(self.script_manager, lambda versions: cb_versions('gcc', versions))
        get_lazbuild_versions(self.script_manager, lambda versions: cb_versions('lazbuild', versions))
        get_java_versions(self.script_manager, lambda versions: cb_versions('java', versions))
        get_mono_versions(self.script_manager, lambda versions: cb_versions('mono', versions))
        get_nodejs_versions(self.script_manager, lambda versions: cb_versions('nodejs', versions))
        get_octave_versions(self.script_manager, lambda versions: cb_versions('octave', versions))
        get_perl_versions(self.script_manager, lambda versions: cb_versions('perl', versions))
        get_php_versions(self.script_manager, lambda versions: cb_versions('php', versions))
        get_python_versions(self.script_manager, lambda versions: cb_versions('python', versions))
        get_ruby_versions(self.script_manager, lambda versions: cb_versions('ruby', versions))
        get_shell_versions(self.script_manager, lambda versions: cb_versions('shell', versions))

    def show_new_program_wizard(self):
        self.button_new.setEnabled(False)

        if self.stacked_container.count() > 1:
            current_widget = self.stacked_container.currentWidget()
        else:
            current_widget = None

        if current_widget != None:
            current_widget.set_program_callbacks_enabled(False)

        identifiers = []

        for i in range(self.tree_programs.topLevelItemCount()):
            identifiers.append(self.tree_programs.topLevelItem(i).data(0, Qt.UserRole).program.identifier)

        context = ProgramWizardContext(self.session, identifiers, self.script_manager, self.image_version, self.executable_versions)

        self.new_program_wizard = ProgramWizardNew(self, context)

        self.new_program_wizard.exec_()

        if self.new_program_wizard.upload_successful:
            self.add_program_to_tree(self.new_program_wizard.program)
            self.tree_programs.topLevelItem(self.tree_programs.topLevelItemCount() - 1).setSelected(True)

            for i in reversed(range(self.tree_programs.topLevelItemCount() - 1)):
                self.tree_programs.topLevelItem(i).setSelected(False)

        if self.tab_is_alive:
            self.new_program_wizard = None

            if current_widget != None:
                current_widget.set_program_callbacks_enabled(True)

            self.button_new.setEnabled(True)

    def purge_selected_program(self):
        selected_items = self.tree_programs.selectedItems()

        if len(selected_items) == 0:
            return

        program_info = selected_items[0].data(0, Qt.UserRole)
        program      = program_info.program
        name         = program.cast_custom_option_value('name', unicode, '<unknown>')
        button       = QMessageBox.question(get_main_window(), 'Delete Program',
                                            u'Deleting program [{0}] is irreversible. All files of this program will be deleted.'.format(name),
                                            QMessageBox.Ok, QMessageBox.Cancel)

        if not self.tab_is_alive or button != QMessageBox.Ok:
            return

        program_info.name_changed.disconnect(self.refresh_program_name)
        program_info.status_changed.disconnect(self.refresh_program_status)

        try:
            program.purge() # FIXME: async_call
        except (Error, REDError) as e:
            QMessageBox.critical(get_main_window(), 'Delete Program Error',
                                 u'Could not delete program [{0}]:\n\n{1}'.format(name, e))
            return

        self.stacked_container.removeWidget(program_info)
        self.tree_programs.takeTopLevelItem(self.tree_programs.indexOfTopLevelItem(selected_items[0]))
        self.update_ui_state()
