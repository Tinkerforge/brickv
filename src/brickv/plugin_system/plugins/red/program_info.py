# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_info.py: Program Info Widget

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

from PyQt4.QtGui import QWidget, QStandardItemModel, QStandardItem, QDialog
from brickv.plugin_system.plugins.red.program_wizard_edit import ProgramWizardEdit
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_info import Ui_ProgramInfo
from brickv.async_call import async_call
import json

class ProgramInfo(QWidget, Ui_ProgramInfo):
    def __init__(self, session, program, script_manager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.session = session
        self.program = program
        self.script_manager = script_manager

        self.edit_arguments_wizard = None

        self.program_dir = unicode(self.program.root_directory)
        self.program_dir_walk_result = None
        self.tree_logs_model = QStandardItemModel(self)
        self.tree_logs_header_labels = ["File", "Time Stamp"]
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)
        self.tree_logs.setModel(self.tree_logs_model)
        self.tree_logs_model.clear()
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)
        parent_stdout = [QStandardItem("STDOUT"), QStandardItem("")]
        parent_stderr = [QStandardItem("STDERR"), QStandardItem("")]
        self.tree_logs_model.appendRow(parent_stdout)
        self.tree_logs_model.appendRow(parent_stderr)

        self.button_refresh.clicked.connect(self.refresh_info)
        self.button_download_log.clicked.connect(self.download_selected_log)
        self.button_delete_log.clicked.connect(self.delete_selected_log)
        self.button_upload_files.clicked.connect(self.upload_files)
        self.button_download_files.clicked.connect(self.download_selected_files)
        self.button_rename_file.clicked.connect(self.rename_selected_file)
        self.button_delete_files.clicked.connect(self.delete_selected_files)
        self.button_edit_language.clicked.connect(self.show_edit_language_wizard)
        self.button_edit_arguments.clicked.connect(self.show_edit_arguments_wizard)
        self.button_edit_stdio.clicked.connect(self.show_edit_stdio_wizard)
        self.button_edit_schedule.clicked.connect(self.show_edit_schedule_wizard)

        self.update_ui_state()

    def refresh_info(self):
        def refresh_async():
            self.program.update()

        def cb_success():
            self.button_refresh.setText("Refresh")
            self.button_refresh.setEnabled(True)
            self.update_ui_state()

        def cb_error():
            self.button_refresh.setText("Error")

        self.button_refresh.setText("Refreshing...")
        self.button_refresh.setEnabled(False)

        async_call(refresh_async, None, cb_success, cb_error)

    def update_ui_state(self):
        #has_logs_selection = len(self.list_logs.selectedItems()) > 0
        has_files_selection = len(self.tree_files.selectedItems()) > 0

        #self.button_download_log.setEnabled(has_logs_selection)
        #self.button_delete_log.setEnabled(has_logs_selection)
        self.button_download_files.setEnabled(has_files_selection)
        self.button_rename_file.setEnabled(len(self.tree_files.selectedItems()) == 1)
        self.button_delete_files.setEnabled(has_files_selection)

        # general
        name = self.program.cast_custom_option_value(Constants.FIELD_NAME, unicode, '<unknown>')
        api_language = self.program.cast_custom_option_value(Constants.FIELD_LANGUAGE, unicode, '<unknown>')

        try:
            language_id = Constants.api_languages.keys()[Constants.api_languages.values().index(api_language)]
            language_display_name = Constants.language_display_names[language_id]
        except:
            language_display_name = '<unknown>'

        self.label_name.setText(name)
        self.label_identifier.setText(str(self.program.identifier))
        self.label_language.setText(language_display_name)

        # logs
        def cb_program_get_os_walk(result):
            if result.stderr == "":
                self.program_dir_walk_result = json.loads(result.stdout)

                for dir_node in self.program_dir_walk_result:
                    if dir_node['root'] == '/'.join([self.program_dir, "log"]):
                        for idx, f in enumerate(dir_node['files']):
                            file_name = f
                            file_path = '/'.join([dir_node['root'], f])
                            f_splitted = f.split('-')
                            time_stamp = f_splitted[0]
                            file_name_tree_logs = f_splitted[1]

                            if file_name_tree_logs.split('.')[0] == "stdout":
                                parent_stdout[0].appendRow([QStandardItem(file_name_tree_logs), QStandardItem(time_stamp)])
                            elif file_name_tree_logs.split('.')[0] == "stderr":
                                parent_stderr[0].appendRow([QStandardItem(file_name_tree_logs), QStandardItem(time_stamp)])

                            print "FILE NAME="+file_name
                            print "FILE PATH="+file_path
                            print "TS="+time_stamp
                            print "FNTG="+file_name_tree_logs
                            print "========================================="

            else:
                # TODO: Error popup for user?
                print result

        self.tree_logs_model.clear()
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)
        parent_stdout = [QStandardItem("STDOUT"), QStandardItem("")]
        parent_stderr = [QStandardItem("STDERR"), QStandardItem("")]
        self.tree_logs_model.appendRow(parent_stdout)
        self.tree_logs_model.appendRow(parent_stderr)

        self.script_manager.execute_script('program_get_os_walk',
                                           cb_program_get_os_walk,
                                           [self.program_dir])

        # arguments
        arguments = []
        editable_arguments_offset = max(self.program.cast_custom_option_value('editable_arguments_offset', int, 0), 0)

        for argument in self.program.arguments.items[editable_arguments_offset:]:
            arguments.append(unicode(argument))

        self.label_arguments.setText('\n'.join(arguments))

        environment = []

        for variable in self.program.environment.items:
            environment.append(unicode(variable))

        self.label_environment.setText('\n'.join(environment))

    def download_selected_log(self):
        #selected_items = self.list_logs.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'download_selected_log', log_filename

    def delete_selected_log(self):
        #selected_items = self.list_logs.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'delete_selected_log', filename

    def upload_files(self):
        print 'upload_files'

    def download_selected_files(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filenames = [unicode(selected_item.text()) for selected_item in selected_items]

        print 'download_selected_files', filenames

    def rename_selected_file(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'rename_selected_file', filename

    def delete_selected_files(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filenames = [unicode(selected_item.text()) for selected_item in selected_items]

        print 'delete_selected_files', filenames

    def show_edit_language_wizard(self):
        print 'show_edit_language_wizard'

    def show_edit_arguments_wizard(self):
        self.button_edit_arguments.setEnabled(False)

        self.edit_arguments_wizard = ProgramWizardEdit(self.session, self.program, [], self.script_manager)
        self.edit_arguments_wizard.finished.connect(self.edit_arguments_wizard_finished)
        self.edit_arguments_wizard.show()

    def edit_arguments_wizard_finished(self, result):
        self.edit_arguments_wizard.finished.disconnect(self.edit_arguments_wizard_finished)

        if result == QDialog.Accepted:
            #self.edit_arguments_wizard
            pass

        self.button_edit_arguments.setEnabled(True)

    def show_edit_stdio_wizard(self):
        print 'show_edit_stdio_wizard'

    def show_edit_schedule_wizard(self):
        print 'show_edit_schedule_wizard'
