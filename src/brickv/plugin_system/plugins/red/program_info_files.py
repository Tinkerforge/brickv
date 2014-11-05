# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_info_files.py: Program Files Info Widget

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

from PyQt4.QtGui import QWidget, QStandardItemModel, QStandardItem
from brickv.plugin_system.plugins.red.ui_program_info_files import Ui_ProgramInfoFiles
from brickv.async_call import async_call
import os
import json

def expand_directory_walk_to_files_list(directory_walk):
    files = []

    def expand(root, dw):
        if 'c' in dw:
            for child_name, child_dw in dw['c'].iteritems():
                expand(os.path.join(root, child_name), child_dw)
        else:
            files.append(root)

    expand('', directory_walk)

    return files


def expand_directory_walk_to_model(directory_walk, parent):
    model = QStandardItemModel(parent)

    def expand(parent_item, name, dw):
        if 'c' in dw:
            if name == None:
                item = parent_item
            else:
                item = QStandardItem(name)
                parent_item.appendRow([item, QStandardItem(''), QStandardItem('')])

            for child_name, child_dw in dw['c'].iteritems():
                expand(item, child_name, child_dw)
        else:
            parent_item.appendRow([QStandardItem(name), QStandardItem(unicode(dw['s'])), QStandardItem(unicode(dw['l']))])

    expand(model.invisibleRootItem(), None, directory_walk)

    return model


class ProgramInfoFiles(QWidget, Ui_ProgramInfoFiles):
    def __init__(self, context, update_main_ui_state, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.script_manager        = context.script_manager
        self.program               = context.program
        self.update_main_ui_state  = update_main_ui_state
        self.root_directory        = unicode(self.program.root_directory)
        self.refresh_in_progress   = False
        self.available_files       = []
        self.available_directories = []

        self.button_upload_files.clicked.connect(self.upload_files)
        self.button_download_files.clicked.connect(self.download_selected_files)
        self.button_rename_file.clicked.connect(self.rename_selected_file)
        self.button_delete_files.clicked.connect(self.delete_selected_files)

    def update_ui_state(self):
        #has_files_selection = len(self.tree_files.selectedItems()) > 0
        #self.set_widget_enabled(self.button_download_files, has_files_selection)
        #self.set_widget_enabled(self.button_rename_file, len(self.tree_files.selectedItems()) == 1)
        #self.set_widget_enabled(self.button_delete_files, has_files_selection)
        pass

    def refresh_files(self):
        def cb_directory_walk(result):
            if result == None or len(result.stderr) > 0:
                self.refresh_in_progress = False
                self.update_main_ui_state()
                return # FIXME: report error

            def expand_async(data):
                directory_walk        = json.loads(data)
                available_files       = []
                available_directories = []

                if directory_walk != None:
                    available_files = sorted(expand_directory_walk_to_files_list(directory_walk))
                    directories     = set()

                    for available_file in available_files:
                        directory = os.path.split(available_file)[0]

                        if len(directory) > 0:
                            directories.add(directory)

                    available_directories = sorted(list(directories))

                return directory_walk, available_files, available_directories

            def cb_expand_success(args):
                directory_walk, available_files, available_directories = args

                self.available_files       = available_files
                self.available_directories = available_directories
                self.refresh_in_progress   = False
                self.update_main_ui_state()

                self.tree_files.setModel(expand_directory_walk_to_model(directory_walk, self))

            def cb_expand_error():
                pass # FIXME: report error

            async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

        self.refresh_in_progress = True
        self.update_main_ui_state()

        self.script_manager.execute_script('directory_walk', cb_directory_walk,
                                           [os.path.join(self.root_directory, 'bin')],
                                           max_len=1024*1024)

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
