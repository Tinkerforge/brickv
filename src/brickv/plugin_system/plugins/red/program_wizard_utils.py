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

from PyQt4.QtCore import Qt, QDir, QVariant
from PyQt4.QtGui import QListWidget, QListWidgetItem, QTreeWidgetItem
from brickv.plugin_system.plugins.red.api import REDProgram
import re
import os
from collections import namedtuple

ProgramWizardContext = namedtuple('ProgramWizardContext', 'session identifiers script_manager image_version_ref')

class Constants:
    PAGE_GENERAL    = 1001
    PAGE_FILES      = 1002
    PAGE_C          = 1003
    PAGE_CSHARP     = 1004
    PAGE_DELPHI     = 1005
    PAGE_JAVA       = 1006
    PAGE_JAVASCRIPT = 1007
    PAGE_OCTAVE     = 1008
    PAGE_PERL       = 1009
    PAGE_PHP        = 1010
    PAGE_PYTHON     = 1011
    PAGE_RUBY       = 1012
    PAGE_SHELL      = 1013
    PAGE_VBNET      = 1014
    PAGE_ARGUMENTS  = 1015
    PAGE_STDIO      = 1016
    PAGE_SCHEDULE   = 1017
    PAGE_SUMMARY    = 1018
    PAGE_UPLOAD     = 1019

    # must match item order in combo_language on general page
    LANGUAGE_INVALID    = 0
    LANGUAGE_C          = 1
    LANGUAGE_CSHARP     = 2
    LANGUAGE_DELPHI     = 3
    LANGUAGE_JAVA       = 4
    LANGUAGE_JAVASCRIPT = 5
    LANGUAGE_OCTAVE     = 6
    LANGUAGE_PERL       = 7
    LANGUAGE_PHP        = 8
    LANGUAGE_PYTHON     = 9
    LANGUAGE_RUBY       = 10
    LANGUAGE_SHELL      = 11
    LANGUAGE_VBNET      = 12

    language_display_names = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_C:          'C/C++',
        LANGUAGE_CSHARP:     'C#',
        LANGUAGE_DELPHI:     'Delphi/Lazarus',
        LANGUAGE_JAVA:       'Java',
        LANGUAGE_JAVASCRIPT: 'JavaScript',
        LANGUAGE_OCTAVE:     'Octave',
        LANGUAGE_PERL:       'Perl',
        LANGUAGE_PHP:        'PHP',
        LANGUAGE_PYTHON:     'Python',
        LANGUAGE_RUBY:       'Ruby',
        LANGUAGE_SHELL:      'Shell',
        LANGUAGE_VBNET:      'Visual Basic .NET'
    }

    language_api_names = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_C:          'c',
        LANGUAGE_CSHARP:     'csharp',
        LANGUAGE_DELPHI:     'delphi',
        LANGUAGE_JAVA:       'java',
        LANGUAGE_JAVASCRIPT: 'javascript',
        LANGUAGE_OCTAVE:     'octave',
        LANGUAGE_PERL:       'perl',
        LANGUAGE_PHP:        'php',
        LANGUAGE_PYTHON:     'python',
        LANGUAGE_RUBY:       'ruby',
        LANGUAGE_SHELL:      'shell',
        LANGUAGE_VBNET:      'vbnet'
    }

    language_pages = {
        LANGUAGE_C:          PAGE_C,
        LANGUAGE_CSHARP:     PAGE_CSHARP,
        LANGUAGE_DELPHI:     PAGE_DELPHI,
        LANGUAGE_JAVA:       PAGE_JAVA,
        LANGUAGE_JAVASCRIPT: PAGE_JAVASCRIPT,
        LANGUAGE_OCTAVE:     PAGE_OCTAVE,
        LANGUAGE_PERL:       PAGE_PERL,
        LANGUAGE_PHP:        PAGE_PHP,
        LANGUAGE_PYTHON:     PAGE_PYTHON,
        LANGUAGE_RUBY:       PAGE_RUBY,
        LANGUAGE_SHELL:      PAGE_SHELL,
        LANGUAGE_VBNET:      PAGE_VBNET
    }

    @staticmethod
    def get_language(language_api_name):
        d = Constants.language_api_names
        return d.keys()[d.values().index(language_api_name)]

    @staticmethod
    def get_language_display_name(language_api_name):
        return Constants.language_display_names[Constants.get_language(language_api_name)]

    @staticmethod
    def get_language_page(language_api_name):
        return Constants.language_pages[Constants.get_language(language_api_name)]

    arguments_help = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_C:          'This list of arguments will be passed to the main() function.',
        LANGUAGE_CSHARP:     'This list of arguments will be passed to the Main() method.',
        LANGUAGE_DELPHI:     'This list of arguments will be available as ParamStr array.',
        LANGUAGE_JAVA:       'This list of arguments will be passed to the main() method.',
        LANGUAGE_JAVASCRIPT: 'This list of arguments will be available as process.argv array.',
        LANGUAGE_OCTAVE:     'This list of arguments can be accessed by calling argv().',
        LANGUAGE_PERL:       'This list of arguments will be available as @ARGV array.',
        LANGUAGE_PHP:        'This list of arguments will be available as $argv array.',
        LANGUAGE_PYTHON:     'This list of arguments will be available as sys.argv list.',
        LANGUAGE_RUBY:       'This list of arguments will be available as ARGV array.',
        LANGUAGE_SHELL:      'This list of arguments will be available as $1 to $n.',
        LANGUAGE_VBNET:      'This list of arguments can be accessed by calling Environment.GetCommandLineArgs()'
    }

    language_file_ending = { # endswith XXX sorted by file ending index
        LANGUAGE_INVALID:    [],
        LANGUAGE_C:          [''],
        LANGUAGE_CSHARP:     ['', '.exe'],
        LANGUAGE_DELPHI:     ['', ('.pas', '.pp')],
        LANGUAGE_JAVA:       ['', '.jar'],
        LANGUAGE_JAVASCRIPT: ['', '.js'],
        LANGUAGE_OCTAVE:     ['', '.m'],
        LANGUAGE_PERL:       ['', '.pl'],
        LANGUAGE_PHP:        ['', ('.php', '.php2', '.php3', '.php4', '.php5')],
        LANGUAGE_PYTHON:     ['', '.py'],
        LANGUAGE_RUBY:       ['', '.rb'],
        LANGUAGE_SHELL:      ['', ('.sh', '.bash')],
        LANGUAGE_VBNET:      ['', '.exe'],
    }

    # must match item order in combo_start_mode on C/C++ page
    C_START_MODE_EXECUTABLE = 0
    C_START_MODE_MAKE = 1

    # must match item order in combo_start_mode on C# page
    CSHARP_START_MODE_EXECUTABLE = 0

    # must match item order in combo_start_mode on Delphi/Lazarus page
    DELPHI_START_MODE_EXECUTABLE = 0
    DELPHI_START_MODE_COMPILE    = 1

    # must match item order in combo_start_mode on Java page
    JAVA_START_MODE_MAIN_CLASS = 0
    JAVA_START_MODE_JAR_FILE   = 1

    # must match item order in combo_start_mode on JavaScript page
    JAVASCRIPT_START_MODE_SCRIPT_FILE = 0
    JAVASCRIPT_START_MODE_COMMAND     = 1

    # must match item order in combo_start_mode on Octave page
    OCTAVE_START_MODE_SCRIPT_FILE = 0

    # must match item order in combo_start_mode on Perl page
    PERL_START_MODE_SCRIPT_FILE = 0
    PERL_START_MODE_COMMAND     = 1

    # must match item order in combo_start_mode on PHP page
    PHP_START_MODE_SCRIPT_FILE = 0
    PHP_START_MODE_COMMAND     = 1

    # must match item order in combo_start_mode on Python page
    PYTHON_START_MODE_SCRIPT_FILE = 0
    PYTHON_START_MODE_MODULE_NAME = 1
    PYTHON_START_MODE_COMMAND     = 2

    # must match item order in combo_start_mode on Ruby page
    RUBY_START_MODE_SCRIPT_FILE = 0
    RUBY_START_MODE_COMMAND     = 1

    # must match item order in combo_start_mode on Shell page
    SHELL_START_MODE_SCRIPT_FILE = 0
    SHELL_START_MODE_COMMAND     = 1

    # must match item order in combo_start_mode on VB.NET page
    VBNET_START_MODE_EXECUTABLE = 0

    # must match item order in combo_stdin_redirection on stdio page
    STDIN_REDIRECTION_DEV_NULL = 0
    STDIN_REDIRECTION_PIPE     = 1
    STDIN_REDIRECTION_FILE     = 2

    api_stdin_redirections = {
        STDIN_REDIRECTION_DEV_NULL: REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDIN_REDIRECTION_PIPE:     REDProgram.STDIO_REDIRECTION_PIPE,
        STDIN_REDIRECTION_FILE:     REDProgram.STDIO_REDIRECTION_FILE
    }

    api_stdin_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL: '/dev/null',
        REDProgram.STDIO_REDIRECTION_PIPE:     'Pipe',
        REDProgram.STDIO_REDIRECTION_FILE:     'File'
    }

    @staticmethod
    def get_stdin_redirection(api_stdin_redirection):
        d = Constants.api_stdin_redirections
        return d.keys()[d.values().index(api_stdin_redirection)]

    @staticmethod
    def get_stdin_redirection_display_name(stdin_redirection):
        return Constants.api_stdin_redirection_display_names[Constants.api_stdin_redirections[stdin_redirection]]

    # must match item order in combo_stdout_redirection on stdio page
    STDOUT_REDIRECTION_DEV_NULL       = 0
    STDOUT_REDIRECTION_FILE           = 1
    STDOUT_REDIRECTION_INDIVIDUAL_LOG = 2
    STDOUT_REDIRECTION_CONTINUOUS_LOG = 3

    api_stdout_redirections = {
        STDOUT_REDIRECTION_DEV_NULL:       REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDOUT_REDIRECTION_FILE:           REDProgram.STDIO_REDIRECTION_FILE,
        STDOUT_REDIRECTION_INDIVIDUAL_LOG: REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG,
        STDOUT_REDIRECTION_CONTINUOUS_LOG: REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG,
    }

    api_stdout_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL:       '/dev/null',
        REDProgram.STDIO_REDIRECTION_FILE:           'File',
        REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG: 'Individual Log Files',
        REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG: 'Continuous Log File'
    }

    @staticmethod
    def get_stdout_redirection(api_stdout_redirection):
        d = Constants.api_stdout_redirections
        return d.keys()[d.values().index(api_stdout_redirection)]

    @staticmethod
    def get_stdout_redirection_display_name(stdout_redirection):
        return Constants.api_stdout_redirection_display_names[Constants.api_stdout_redirections[stdout_redirection]]

    # must match item order in combo_stderr_redirection on stdio page
    STDERR_REDIRECTION_DEV_NULL       = 0
    STDERR_REDIRECTION_FILE           = 1
    STDERR_REDIRECTION_INDIVIDUAL_LOG = 2
    STDERR_REDIRECTION_CONTINUOUS_LOG = 3
    STDERR_REDIRECTION_STDOUT         = 4

    api_stderr_redirections = {
        STDERR_REDIRECTION_DEV_NULL:       REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDERR_REDIRECTION_FILE:           REDProgram.STDIO_REDIRECTION_FILE,
        STDERR_REDIRECTION_INDIVIDUAL_LOG: REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG,
        STDERR_REDIRECTION_CONTINUOUS_LOG: REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG,
        STDERR_REDIRECTION_STDOUT:         REDProgram.STDIO_REDIRECTION_STDOUT
    }

    api_stderr_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL:       '/dev/null',
        REDProgram.STDIO_REDIRECTION_FILE:           'File',
        REDProgram.STDIO_REDIRECTION_INDIVIDUAL_LOG: 'Individual Log Files',
        REDProgram.STDIO_REDIRECTION_CONTINUOUS_LOG: 'Continuous Log File',
        REDProgram.STDIO_REDIRECTION_STDOUT:         'Standard Output'
    }

    @staticmethod
    def get_stderr_redirection(api_stderr_redirection):
        d = Constants.api_stderr_redirections
        return d.keys()[d.values().index(api_stderr_redirection)]

    @staticmethod
    def get_stderr_redirection_display_name(stderr_redirection):
        return Constants.api_stderr_redirection_display_names[Constants.api_stderr_redirections[stderr_redirection]]

    # must match item order in combo_start_condition on schedule page
    START_CONDITION_NEVER  = 0
    START_CONDITION_NOW    = 1
    START_CONDITION_REBOOT = 2
    START_CONDITION_TIME   = 3
    START_CONDITION_CRON   = 4

    api_start_conditions = {
        START_CONDITION_NEVER:  REDProgram.START_CONDITION_NEVER,
        START_CONDITION_NOW:    REDProgram.START_CONDITION_NOW,
        START_CONDITION_REBOOT: REDProgram.START_CONDITION_REBOOT,
        START_CONDITION_TIME:   REDProgram.START_CONDITION_TIMESTAMP,
        START_CONDITION_CRON:   REDProgram.START_CONDITION_CRON
    }

    api_start_condition_display_names = {
        REDProgram.START_CONDITION_NEVER:     'Never',
        REDProgram.START_CONDITION_NOW:       'Now',
        REDProgram.START_CONDITION_REBOOT:    'Reboot',
        REDProgram.START_CONDITION_TIMESTAMP: 'Time',
        REDProgram.START_CONDITION_CRON:      'Cron'
    }

    @staticmethod
    def get_start_condition(api_start_condition):
        d = Constants.api_start_conditions
        return d.keys()[d.values().index(api_start_condition)]

    @staticmethod
    def get_start_condition_display_name(start_condition):
        return Constants.api_start_condition_display_names[Constants.api_start_conditions[start_condition]]

    # must match item order in combo_repeat_mode on schedule page
    REPEAT_MODE_NEVER    = 0
    REPEAT_MODE_INTERVAL = 1
    REPEAT_MODE_CRON     = 2

    api_repeat_modes = {
        REPEAT_MODE_NEVER:    REDProgram.REPEAT_MODE_NEVER,
        REPEAT_MODE_INTERVAL: REDProgram.REPEAT_MODE_INTERVAL,
        REPEAT_MODE_CRON:     REDProgram.REPEAT_MODE_CRON,
    }

    api_repeat_mode_display_names = {
        REDProgram.REPEAT_MODE_NEVER:    'Never',
        REDProgram.REPEAT_MODE_INTERVAL: 'Interval',
        REDProgram.REPEAT_MODE_CRON:     'Cron'
    }

    @staticmethod
    def get_repeat_mode(api_repeat_mode):
        d = Constants.api_repeat_modes
        return d.keys()[d.values().index(api_repeat_mode)]

    @staticmethod
    def get_repeat_mode_display_name(repeat_mode):
        return Constants.api_repeat_mode_display_names[Constants.api_repeat_modes[repeat_mode]]

    api_scheduler_state_display_name = {
        REDProgram.SCHEDULER_STATE_STOPPED:                      'Stopped',
        REDProgram.SCHEDULER_STATE_WAITING_FOR_START_CONDITION:  'Waiting for start condition',
        REDProgram.SCHEDULER_STATE_DELAYING_START:               'Delaying start',
        REDProgram.SCHEDULER_STATE_WAITING_FOR_REPEAT_CONDITION: 'Waiting for repeat condition',
        REDProgram.SCHEDULER_STATE_ERROR_OCCURRED:               'Error occurred'
    }

    DEFAULT_C_START_MODE          = C_START_MODE_EXECUTABLE
    DEFAULT_CSHARP_START_MODE     = CSHARP_START_MODE_EXECUTABLE
    DEFAULT_DELPHI_START_MODE     = DELPHI_START_MODE_EXECUTABLE
    DEFAULT_JAVA_START_MODE       = JAVA_START_MODE_MAIN_CLASS
    DEFAULT_JAVASCRIPT_START_MODE = JAVASCRIPT_START_MODE_SCRIPT_FILE
    DEFAULT_OCTAVE_START_MODE     = OCTAVE_START_MODE_SCRIPT_FILE
    DEFAULT_PERL_START_MODE       = PERL_START_MODE_SCRIPT_FILE
    DEFAULT_PHP_START_MODE        = PHP_START_MODE_SCRIPT_FILE
    DEFAULT_PYTHON_START_MODE     = PYTHON_START_MODE_SCRIPT_FILE
    DEFAULT_RUBY_START_MODE       = RUBY_START_MODE_SCRIPT_FILE
    DEFAULT_SHELL_START_MODE      = SHELL_START_MODE_SCRIPT_FILE
    DEFAULT_VBNET_START_MODE      = VBNET_START_MODE_EXECUTABLE
    DEFAULT_STDIN_REDIRECTION     = STDIN_REDIRECTION_PIPE
    DEFAULT_STDOUT_REDIRECTION    = STDOUT_REDIRECTION_CONTINUOUS_LOG
    DEFAULT_STDERR_REDIRECTION    = STDERR_REDIRECTION_STDOUT
    DEFAULT_START_CONDITION       = START_CONDITION_NOW
    DEFAULT_REPEAT_MODE           = REPEAT_MODE_NEVER


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
    def __init__(self, label_items, list_items, label_items_help,
                 button_add_item, button_remove_item,
                 button_up_item, button_down_item, new_item_text):
        self.label_items        = label_items
        self.list_items         = list_items
        self.label_items_help   = label_items_help
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

    def set_visible(self, visible):
        self.label_items.setVisible(visible)
        self.list_items.setVisible(visible)
        self.label_items_help.setVisible(visible)
        self.button_add_item.setVisible(visible)
        self.button_remove_item.setVisible(visible)
        self.button_up_item.setVisible(visible)
        self.button_down_item.setVisible(visible)

    def add_item(self, text, edit_item=False):
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.list_items.addItem(item)

        if edit_item:
            self.list_items.editItem(item)

        self.update_ui_state()

    def add_new_item(self):
        counter = self.new_item_counter
        self.new_item_counter += 1

        self.add_item(self.new_item_text.format(counter), edit_item=True)

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

    def clear(self):
        self.new_item_counter = 1

        self.list_items.clear()

    def reset(self):
        self.clear()

        for original_item in self.original_items:
            self.add_item(original_item)

    def get_items(self):
        items = []

        for row in range(self.list_items.count()):
            items.append(unicode(self.list_items.item(row).text()))

        return items


class TreeWidgetEditor:
    def __init__(self, label_items, tree_items, label_items_help,
                 button_add_item, button_remove_item,
                 button_up_item, button_down_item, new_item_texts):
        self.label_items        = label_items
        self.tree_items         = tree_items
        self.label_items_help   = label_items_help
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
            child = root.child(row)
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

    def set_visible(self, visible):
        self.label_items.setVisible(visible)
        self.tree_items.setVisible(visible)
        self.label_items_help.setVisible(visible)
        self.button_add_item.setVisible(visible)
        self.button_remove_item.setVisible(visible)
        self.button_up_item.setVisible(visible)
        self.button_down_item.setVisible(visible)

    def add_item(self, texts, edit_item=False):
        item = QTreeWidgetItem(texts)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        self.tree_items.addTopLevelItem(item)

        if edit_item:
            self.tree_items.editItem(item)

        self.update_ui_state()

    def add_new_item(self):
        texts = []

        for text in self.new_item_texts:
            texts.append(text.format(self.new_item_counter))

        self.new_item_counter += 1

        self.add_item(texts, edit_item=True)

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

    def clear(self):
        self.new_item_counter = 1

        self.tree_items.invisibleRootItem().takeChildren()

    def reset(self):
        self.clear()

        for original_item in self.original_items:
            self.add_item(original_item)

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
    def __init__(self, page, edit, label, regexp=None): # FIXME: swap edit and label
        self.page     = page
        self.edit     = edit
        self.label    = label
        self.regexp   = None
        self.complete = False

        if regexp != None:
            self.regexp = re.compile(regexp)

        self.edit.textChanged.connect(lambda: self.check(True))

        self.check(False)

    def check(self, emit):
        was_complete = self.complete
        text = unicode(self.edit.text())
        self.complete = len(text) > 0

        if self.complete and self.regexp != None:
            self.complete = self.regexp.match(text) != None

        if self.complete:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_complete != self.complete:
            self.page.completeChanged.emit()


class MandatoryEditableComboBoxChecker:
    def __init__(self, page, combo, label): # FIXME: swap combo and label
        self.page     = page
        self.combo    = combo
        self.label    = label
        self.complete = False

        self.combo.currentIndexChanged.connect(lambda: self.check(True))
        self.combo.editTextChanged.connect(lambda: self.check(True))

        self.check(False)

    def check(self, emit):
        was_complete = self.complete
        self.complete = len(self.combo.currentText()) > 0

        if self.complete:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_complete != self.complete:
            self.page.completeChanged.emit()


# expects the combo box to be editable
# FIXME: ensure that file is relative, non-empty and does not start with ..
class MandatoryTypedFileSelector:
    def __init__(self, page, label_file, combo_file, label_type, combo_type, label_help):
        self.page       = page
        self.label_file = label_file
        self.combo_file = combo_file
        self.label_type = label_type
        self.combo_type = combo_type
        self.label_help = label_help

        # FIXME
        self.c1 = MandatoryEditableComboBoxChecker(page, combo_file, label_file)
        self.c2 = ComboBoxFileEndingChecker(page, combo_file, combo_type)

    def set_visible(self, visible):
        self.label_file.setVisible(visible)
        self.combo_file.setVisible(visible)
        self.label_type.setVisible(visible)
        self.combo_type.setVisible(visible)
        self.label_help.setVisible(visible)

    def reset(self):
        self.c2.check(False)
        self.combo_type.setCurrentIndex(1) # FIXME

    @property
    def complete(self):
        return self.c1.complete


# expects the combo box to be editable
class MandatoryDirectorySelector:
    def __init__(self, page, combo, label):
        self.page  = page
        self.combo = combo
        self.label = label
        self.complete = False
        self.original_items = []

        for i in range(combo.count()):
            self.original_items.append(unicode(combo.itemText(i)))

        self.combo.currentIndexChanged.connect(lambda: self.check(True))
        self.combo.editTextChanged.connect(lambda: self.check(True))

    def set_visible(self, visible):
        self.combo.setVisible(visible)
        self.label.setVisible(visible)

    def set_current_text(self, text):
        if len(text) == 0:
            return

        i = self.combo.findText(text)

        if i < 0:
            self.combo.addItem(text)
            i = self.combo.count() - 1

        self.combo.setCurrentIndex(i)

    def reset(self):
        self.combo.clear()
        self.combo.addItems(self.original_items)
        self.combo.addItems(self.page.wizard().available_directories)

        if self.combo.count() > 1 and len(self.original_items) > 0 and self.original_items[0] != '.':
            self.combo.clearEditText()

    # ensure that directory is relative, non-empty and does not start with ..
    def check(self, emit):
        was_complete  = self.complete
        directory     = unicode(QDir.cleanPath(os.path.join(unicode(self.combo.currentText()), '.')))
        self.complete = len(directory) > 0 and \
                        not directory.startswith('/') and \
                        directory != './..' and \
                        not directory.startswith('./../') and \
                        directory != '..' and \
                        not directory.startswith('../')

        if self.complete:
            self.label.setStyleSheet('')
        else:
            self.label.setStyleSheet('QLabel { color : red }')

        if emit and was_complete != self.complete:
            self.page.completeChanged.emit()


class ComboBoxFileEndingChecker:
    class NoEndingCheckRequired:
        class NoIndexChangeRequired:
            def connect(self, *args, **kwargs):
                return
        currentIndexChanged = NoIndexChangeRequired()
        def currentIndex(self):
            return 0 # = *

    def __init__(self, page, combo_file, combo_ending = None):
        self.page       = page
        self.combo_file = combo_file
        if combo_ending == None:
            self.combo_ending = self.NoEndingCheckRequired()
        else:
            self.combo_ending = combo_ending

        self.combo_ending.currentIndexChanged.connect(lambda: self.check(True))

    def check(self, emit):
        self.combo_file.clear()
        self.combo_file.clearEditText()

        ends = Constants.language_file_ending[self.page.language][self.combo_ending.currentIndex()]

        for filename in sorted(self.page.wizard().available_files):
            if type(ends) != tuple:
                ends = (ends,)
            for end in ends:
                if filename.lower().endswith(end):
                    self.combo_file.addItem(filename)

        if self.combo_file.count() > 1:
            self.combo_file.clearEditText()


def set_current_combo_index_from_data(combo, data):
    i = combo.findData(QVariant(data))

    if i >= 0:
        combo.setCurrentIndex(i)
    else:
        combo.addItem('<unknown>', QVariant(data))
        combo.setCurrentIndex(combo.count() - 1)
