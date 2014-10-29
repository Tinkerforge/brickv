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
import re
from collections import namedtuple

ProgramWizardContext = namedtuple('ProgramWizardContext', ['session', 'identifiers', 'script_manager', 'image_version_ref'])

class Constants:
    PAGE_GENERAL    = 0
    PAGE_FILES      = 1
    PAGE_JAVA       = 2
    PAGE_PYTHON     = 3
    PAGE_ARGUMENTS  = 4
    PAGE_STDIO      = 5
    PAGE_SCHEDULE   = 6
    PAGE_SUMMARY    = 7
    PAGE_UPLOAD     = 8
    PAGE_RUBY       = 9
    PAGE_SHELL      = 10
    PAGE_PERL       = 11
    PAGE_PHP        = 12
    PAGE_OCTAVE     = 13
    PAGE_JAVASCRIPT = 14
    PAGE_CSHARP     = 15
    PAGE_VBNET      = 16

    FIELD_NAME     = 'name'
    FIELD_LANGUAGE = 'language'

    # must match item order in combo_language on general page
    LANGUAGE_INVALID    = 0
    LANGUAGE_CSHARP     = 1
    LANGUAGE_JAVA       = 2
    LANGUAGE_JAVASCRIPT = 3
    LANGUAGE_OCTAVE     = 4
    LANGUAGE_PERL       = 5
    LANGUAGE_PHP        = 6
    LANGUAGE_PYTHON     = 7
    LANGUAGE_RUBY       = 8
    LANGUAGE_SHELL      = 9
    LANGUAGE_VBNET      = 10

    language_display_names = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_CSHARP:     'C#',
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

    api_languages = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_CSHARP:     'csharp',
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

    @staticmethod
    def get_language(api_language):
        d = Constants.api_languages
        return d.keys()[d.values().index(api_language)]

    arguments_help = {
        LANGUAGE_INVALID:    '<invalid>',
        LANGUAGE_CSHARP:     'This list of arguments will be passed to the Main() method.',
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
        LANGUAGE_CSHARP:     ['', '.exe'],
        LANGUAGE_JAVA:       ['', '.java'],
        LANGUAGE_JAVASCRIPT: ['', '.js'],
        LANGUAGE_OCTAVE:     ['', '.m'],
        LANGUAGE_PERL:       ['', '.pl'],
        LANGUAGE_PHP:        ['', ('.php', '.php2', '.php3', '.php4', '.php5')],
        LANGUAGE_PYTHON:     ['', '.py'],
        LANGUAGE_RUBY:       ['', '.rb'],
        LANGUAGE_SHELL:      ['', ('.sh', '.bash')],
        LANGUAGE_VBNET:      ['', '.exe'],
    }
    
    # must match item order in combo_start_mode on C# page
    CSHARP_START_MODE_EXECUTABLE = 0

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
    STDOUT_REDIRECTION_DEV_NULL = 0
    STDOUT_REDIRECTION_FILE     = 1
    STDOUT_REDIRECTION_LOG      = 2

    api_stdout_redirections = {
        STDOUT_REDIRECTION_DEV_NULL: REDProgram.STDIO_REDIRECTION_DEV_NULL,
        STDOUT_REDIRECTION_FILE:     REDProgram.STDIO_REDIRECTION_FILE,
        STDOUT_REDIRECTION_LOG:      REDProgram.STDIO_REDIRECTION_LOG
    }

    api_stdout_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL: '/dev/null',
        REDProgram.STDIO_REDIRECTION_FILE:     'File',
        REDProgram.STDIO_REDIRECTION_LOG:      'Automatic Log File'
    }

    @staticmethod
    def get_stdout_redirection(api_stdout_redirection):
        d = Constants.api_stdout_redirections
        return d.keys()[d.values().index(api_stdout_redirection)]

    @staticmethod
    def get_stdout_redirection_display_name(stdout_redirection):
        return Constants.api_stdout_redirection_display_names[Constants.api_stdout_redirections[stdout_redirection]]

    # must match item order in combo_stderr_redirection on stdio page
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

    api_stderr_redirection_display_names = {
        REDProgram.STDIO_REDIRECTION_DEV_NULL: '/dev/null',
        REDProgram.STDIO_REDIRECTION_FILE:     'File',
        REDProgram.STDIO_REDIRECTION_LOG:      'Automatic Log File',
        REDProgram.STDIO_REDIRECTION_STDOUT:   'Standard Output'
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

    api_start_conditions = {
        START_CONDITION_NEVER:  REDProgram.START_CONDITION_NEVER,
        START_CONDITION_NOW:    REDProgram.START_CONDITION_NOW,
        START_CONDITION_REBOOT: REDProgram.START_CONDITION_REBOOT,
        START_CONDITION_TIME:   REDProgram.START_CONDITION_TIMESTAMP
    }

    api_start_condition_display_names = {
        REDProgram.START_CONDITION_NEVER:     'Never',
        REDProgram.START_CONDITION_NOW:       'Now',
        REDProgram.START_CONDITION_REBOOT:    'Reboot',
        REDProgram.START_CONDITION_TIMESTAMP: 'Time'
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

    DEFAULT_CSHARP_START_MODE     = CSHARP_START_MODE_EXECUTABLE
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
    DEFAULT_STDOUT_REDIRECTION    = STDOUT_REDIRECTION_LOG
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

    def reset_items(self):
        self.new_item_counter = 1

        self.list_items.clear()

        for original_item in self.original_items:
            self.add_item(original_item)

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

    def reset_items(self):
        self.new_item_counter = 1

        self.tree_items.invisibleRootItem().takeChildren()

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
    def __init__(self, page, edit, label, regexp=None):
        self.page = page
        self.edit = edit
        self.label = label
        self.regexp = None
        self.valid = False

        if regexp != None:
            self.regexp = re.compile(regexp)

        self.edit.textChanged.connect(lambda: self.check(True))

        self.check(False)

    def check(self, emit):
        was_valid = self.valid
        text = unicode(self.edit.text())
        self.valid = len(text) > 0

        if self.valid and self.regexp != None:
            self.valid = self.regexp.match(text) != None

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

# FIXME: merge with MandatoryEditableComboBoxChecker into MandatoryFileSelector
class ComboBoxFileEndingChecker:
    def __init__(self, page, combo_file, combo_ending):
        self.page         = page
        self.combo_file   = combo_file
        self.combo_ending = combo_ending

        self.combo_ending.currentIndexChanged.connect(lambda: self.check(True))

    def check(self, emit):
        self.combo_file.clear()

        ends = Constants.language_file_ending[self.page.language][self.combo_ending.currentIndex()]

        for filename in sorted(self.page.wizard().available_files):
            if type(ends) != tuple:
                ends = (ends,)
            for end in ends:
                if filename.lower().endswith(end):
                    self.combo_file.addItem(filename)
