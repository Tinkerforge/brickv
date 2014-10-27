# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_wizard_utils.py: Program Wizard Utils

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
from PyQt4.QtGui import QListWidget, QListWidgetItem, QTreeWidgetItem
from brickv.plugin_system.plugins.red.api import REDProgram

class Constants:
    PAGE_GENERAL   = 0
    PAGE_FILES     = 1
    PAGE_JAVA      = 2
    PAGE_PYTHON    = 3
    PAGE_ARGUMENTS = 4
    PAGE_STDIO     = 5
    PAGE_SCHEDULE  = 6
    PAGE_SUMMARY   = 7
    PAGE_UPLOAD    = 8

    FIELD_NAME     = 'name'
    FIELD_LANGUAGE = 'language'

    LANGUAGE_INVALID = 0
    LANGUAGE_JAVA    = 1
    LANGUAGE_PYTHON  = 2

    language_display_names = {
        LANGUAGE_INVALID: '<invalid>',
        LANGUAGE_JAVA:    'Java',
        LANGUAGE_PYTHON:  'Python'
    }

    api_languages = {
        LANGUAGE_INVALID: '<invalid>',
        LANGUAGE_JAVA:    'java',
        LANGUAGE_PYTHON:  'python'
    }

    arguments_help = {
        LANGUAGE_INVALID: '<invalid>',
        LANGUAGE_JAVA:    'This list of arguments will be passed to the main() method.',
        LANGUAGE_PYTHON:  'This list of arguments will be available as the sys.argv list.'
    }

    environment_help = {
        LANGUAGE_INVALID: '<invalid>',
        LANGUAGE_JAVA:    'This list of environment variables will be set for the Java program.',
        LANGUAGE_PYTHON:  'This list of environment variables will be set for the Python program.',
    }

    JAVA_START_MODE_MAIN_CLASS = 0
    JAVA_START_MODE_JAR_FILE   = 1

    PYTHON_START_MODE_SCRIPT_FILE = 0
    PYTHON_START_MODE_MODULE_NAME = 1
    PYTHON_START_MODE_COMMAND     = 2

    STDIN_REDIRECTION_DEV_NULL = 0
    STDIN_REDIRECTION_PIPE     = 1
    STDIN_REDIRECTION_FILE     = 2

    api_stdin_redirections = {
        STDIN_REDIRECTION_DEV_NULL: REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDIN_REDIRECTION_PIPE:     REDProgram.STDIO_REDIRECTION_PIPE,
        STDIN_REDIRECTION_FILE:     REDProgram.STDIO_REDIRECTION_FILE
    }

    STDOUT_REDIRECTION_DEV_NULL = 0
    STDOUT_REDIRECTION_FILE     = 1
    STDOUT_REDIRECTION_LOG      = 2

    api_stdout_redirections = {
        STDOUT_REDIRECTION_DEV_NULL: REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDOUT_REDIRECTION_FILE:     REDProgram.STDIO_REDIRECTION_FILE,
        STDOUT_REDIRECTION_LOG:      REDProgram.STDIO_REDIRECTION_LOG
    }

    STDERR_REDIRECTION_DEV_NULL = 0
    STDERR_REDIRECTION_FILE     = 1
    STDERR_REDIRECTION_LOG      = 2
    STDERR_REDIRECTION_STDOUT   = 3

    api_stderr_redirections = {
        STDERR_REDIRECTION_DEV_NULL: REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDERR_REDIRECTION_FILE:     REDProgram.STDIO_REDIRECTION_FILE,
        STDERR_REDIRECTION_LOG:      REDProgram.STDIO_REDIRECTION_LOG,
        STDERR_REDIRECTION_STDOUT:   REDProgram.STDIO_REDIRECTION_STDOUT
    }

    SCHEDULE_START_CONDITION_NEVER  = 0
    SCHEDULE_START_CONDITION_NOW    = 1
    SCHEDULE_START_CONDITION_REBOOT = 2
    SCHEDULE_START_CONDITION_TIME   = 3

    api_schedule_start_condition = {
        SCHEDULE_START_CONDITION_NEVER:  REDProgram.START_CONDITION_NEVER,
        SCHEDULE_START_CONDITION_NOW:    REDProgram.START_CONDITION_NOW,
        SCHEDULE_START_CONDITION_REBOOT: REDProgram.START_CONDITION_REBOOT,
        SCHEDULE_START_CONDITION_TIME:   REDProgram.START_CONDITION_TIMESTAMP
    }

    SCHEDULE_REPEAT_MODE_NEVER     = 0
    SCHEDULE_REPEAT_MODE_INTERVAL  = 1
    SCHEDULE_REPEAT_MODE_SELECTION = 2

    api_schedule_repeat_mode = {
        SCHEDULE_REPEAT_MODE_NEVER:     REDProgram.REPEAT_MODE_NEVER,
        SCHEDULE_REPEAT_MODE_INTERVAL:  REDProgram.REPEAT_MODE_INTERVAL,
        SCHEDULE_REPEAT_MODE_SELECTION: REDProgram.REPEAT_MODE_SELECTION,
    }

    DEFAULT_JAVA_START_MODE          = JAVA_START_MODE_MAIN_CLASS
    DEFAULT_PYTHON_START_MODE        = PYTHON_START_MODE_SCRIPT_FILE
    DEFAULT_STDIN_REDIRECTION        = STDIN_REDIRECTION_PIPE
    DEFAULT_STDOUT_REDIRECTION       = STDOUT_REDIRECTION_LOG
    DEFAULT_STDERR_REDIRECTION       = STDERR_REDIRECTION_STDOUT
    DEFAULT_SCHEDULE_START_CONDITION = SCHEDULE_START_CONDITION_NOW
    DEFAULT_SCHEDULE_REPEAT_MODE     = SCHEDULE_REPEAT_MODE_NEVER


# workaround miscalculated initial size-hint for initially hidden QListWidgets
class ExpandingListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        QListWidget.__init__(self, *args, **kwargs)

    # overrides QListWidget.sizeHint
    def sizeHint(self):
        size = QListWidget.sizeHint(self)

        if size.height() < 2000:
            size.setHeight(2000)

        return size


class ListWidgetEditor:
    def __init__(self, list_items, button_add_item, button_remove_item,
                 button_up_item, button_down_item, new_item_text):
        self.list_items         = list_items
        self.button_add_item    = button_add_item
        self.button_remove_item = button_remove_item
        self.button_up_item     = button_up_item
        self.button_down_item   = button_down_item
        self.new_item_text      = new_item_text
        self.new_item_counter   = 1

        self.list_items.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_item.clicked.connect(self.add_new_item)
        self.button_remove_item.clicked.connect(self.remove_selected_item)
        self.button_up_item.clicked.connect(self.up_selected_item)
        self.button_down_item.clicked.connect(self.down_selected_item)

        self.original_items = []

        for row in range(self.list_items.count()):
            self.original_items.append(unicode(self.list_items.item(row).text()))

    def update_ui_state(self):
        has_selection = len(self.list_items.selectedItems()) > 0
        item_count = self.list_items.count()

        if has_selection:
            selected_index = self.list_items.row(self.list_items.selectedItems()[0])
        else:
            selected_index = -1

        self.button_remove_item.setEnabled(has_selection)
        self.button_up_item.setEnabled(item_count > 1 and has_selection and selected_index > 0)
        self.button_down_item.setEnabled(item_count > 1 and has_selection and selected_index < item_count - 1)

    def add_new_item(self):
        item = QListWidgetItem(self.new_item_text.format(self.new_item_counter))
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.new_item_counter += 1

        self.list_items.addItem(item)
        self.list_items.editItem(item)
        self.update_ui_state()

    def remove_selected_item(self):
        for item in self.list_items.selectedItems():
            self.list_items.takeItem(self.list_items.row(item))

        self.update_ui_state()

    def up_selected_item(self):
        selected_items = self.list_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.list_items.row(selected_items[0])
        item = self.list_items.takeItem(row)

        self.list_items.insertItem(row - 1, item)
        self.list_items.setCurrentRow(row - 1)

    def down_selected_item(self):
        selected_items = self.list_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.list_items.row(selected_items[0])
        item = self.list_items.takeItem(row)

        self.list_items.insertItem(row + 1, item)
        self.list_items.setCurrentRow(row + 1)

    def reset_items(self):
        self.new_item_counter = 1

        self.list_items.clear()

        for original_item in self.original_items:
            item = QListWidgetItem(original_item)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.list_items.addItem(item)

        self.update_ui_state()

    def get_items(self):
        items = []

        for row in range(self.list_items.count()):
            items.append(unicode(self.list_items.item(row).text()))

        return items


class TreeWidgetEditor:
    def __init__(self, tree_items, button_add_item, button_remove_item,
                 button_up_item, button_down_item, new_item_texts):
        self.tree_items         = tree_items
        self.button_add_item    = button_add_item
        self.button_remove_item = button_remove_item
        self.button_up_item     = button_up_item
        self.button_down_item   = button_down_item
        self.new_item_texts     = new_item_texts
        self.new_item_counter   = 1

        self.tree_items.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_item.clicked.connect(self.add_new_item)
        self.button_remove_item.clicked.connect(self.remove_selected_item)
        self.button_up_item.clicked.connect(self.up_selected_item)
        self.button_down_item.clicked.connect(self.down_selected_item)

        self.original_items = []

        root = self.tree_items.invisibleRootItem()

        for row in range(root.childCount()):
            child = self.tree_items.child(row)
            item = []

            for column in range(child.columnCount()):
                item.append(unicode(child.text(column)))

            self.original_items.append(item)

    def update_ui_state(self):
        has_selection = len(self.tree_items.selectedItems()) > 0
        item_count = self.tree_items.invisibleRootItem().childCount()

        if has_selection:
            selected_index = self.tree_items.indexOfTopLevelItem(self.tree_items.selectedItems()[0])
        else:
            selected_index = -1

        self.button_remove_item.setEnabled(has_selection)
        self.button_up_item.setEnabled(item_count > 1 and has_selection and selected_index > 0)
        self.button_down_item.setEnabled(item_count > 1 and has_selection and selected_index < item_count - 1)

    def add_new_item(self):
        texts = []

        for text in self.new_item_texts:
            texts.append(text.format(self.new_item_counter))

        self.new_item_counter += 1

        item = QTreeWidgetItem(texts)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.tree_items.addTopLevelItem(item)
        self.tree_items.editItem(item)
        self.update_ui_state()

    def remove_selected_item(self):
        for item in self.tree_items.selectedItems():
            row = self.tree_items.indexOfTopLevelItem(item)
            self.tree_items.takeTopLevelItem(row)

        self.update_ui_state()

    def up_selected_item(self):
        selected_items = self.tree_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.tree_items.indexOfTopLevelItem(selected_items[0])
        item = self.tree_items.takeTopLevelItem(row)

        self.tree_items.insertTopLevelItem(row - 1, item)
        self.tree_items.setCurrentItem(item)

    def down_selected_item(self):
        selected_items = self.tree_items.selectedItems()

        if len(selected_items) == 0:
            return

        row = self.tree_items.indexOfTopLevelItem(selected_items[0])
        item = self.tree_items.takeTopLevelItem(row)

        self.tree_items.insertTopLevelItem(row + 1, item)
        self.tree_items.setCurrentItem(item)

    def reset_items(self):
        self.new_item_counter = 1

        self.tree_items.invisibleRootItem().takeChildren()

        for original_item in self.original_items:
            item = QTreeWidgetItem(original_item)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.tree_items.addTopLevelItem(item)

        self.update_ui_state()

    def get_items(self):
        items = []

        for row in range(self.tree_items.topLevelItemCount()):
            child = self.tree_items.topLevelItem(row)
            item = []

            for column in range(child.columnCount()):
                item.append(unicode(child.text(column)))

            items.append(item)

        return items


class MandatoryLineEditChecker:
    def __init__(self, page, edit, label):
        self.page = page
        self.edit = edit
        self.label = label
        self.valid = False

        self.edit.textChanged.connect(lambda: self.check(True))

        self.check(False)

    def check(self, emit):
        was_valid = self.valid
        self.valid = len(self.edit.text()) > 0

        if self.valid:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_valid != self.valid:
            self.page.completeChanged.emit()


class MandatoryEditableComboBoxChecker:
    def __init__(self, page, combo, label):
        self.page  = page
        self.combo = combo
        self.label = label
        self.valid = False

        self.combo.currentIndexChanged.connect(lambda: self.check(True))
        self.combo.editTextChanged.connect(lambda: self.check(True))

        self.check(False)

    def check(self, emit):
        was_valid = self.valid
        self.valid = len(self.combo.currentText()) > 0

        if self.valid:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_valid != self.valid:
            self.page.completeChanged.emit()
