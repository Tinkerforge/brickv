# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_ruby.py: Program Wizard Ruby Page

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

from PyQt4.QtCore import QVariant
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_ruby import Ui_ProgramPageRuby

def get_ruby_versions(script_manager, callback):
    def cb_versions(result):
        if result != None:
            try:
                version = result.stdout.split('\n')[0].split(' ')[1]
                callback([ExecutableVersion('/usr/bin/ruby', version)])
                return
            except:
                pass

        # Could not get versions, we assume that some version of ruby 1.9 is installed
        callback([ExecutableVersion('/usr/bin/ruby', '1.9')])

    script_manager.execute_script('ruby_versions', cb_versions)


class ProgramPageRuby(ProgramPage, Ui_ProgramPageRuby):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_RUBY

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('ruby.version', self.combo_version)
        self.registerField('ruby.start_mode', self.combo_start_mode)
        self.registerField('ruby.script_file', self.combo_script_file, 'currentText')
        self.registerField('ruby.command', self.edit_command)
        self.registerField('ruby.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.combo_script_file_selector       = MandatoryTypedFileSelector(self,
                                                                           self.label_script_file,
                                                                           self.combo_script_file,
                                                                           self.label_script_file_type,
                                                                           self.combo_script_file_type,
                                                                           self.label_script_file_help)
        self.edit_command_checker             = MandatoryLineEditChecker(self,
                                                                         self.edit_command,
                                                                         self.label_command)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self,
                                                                           self.combo_working_directory,
                                                                           self.label_working_directory)
        self.option_list_editor               = ListWidgetEditor(self.label_options,
                                                                 self.list_options,
                                                                 self.label_options_help,
                                                                 self.button_add_option,
                                                                 self.button_remove_option,
                                                                 self.button_up_option,
                                                                 self.button_down_option,
                                                                 '<new Ruby option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        self.update_combo_version('ruby', self.combo_version)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_RUBY_START_MODE)
        self.combo_script_file_selector.reset()
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            self.combo_working_directory_selector.set_current_text(unicode(program.working_directory))

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('ruby.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if start_mode == Constants.RUBY_START_MODE_SCRIPT_FILE and \
           not self.combo_script_file_selector.complete:
            return False

        if start_mode == Constants.RUBY_START_MODE_COMMAND and \
           not self.edit_command_checker.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_ui_state(self):
        start_mode             = self.get_field('ruby.start_mode').toInt()[0]
        start_mode_script_file = start_mode == Constants.RUBY_START_MODE_SCRIPT_FILE
        start_mode_command     = start_mode == Constants.RUBY_START_MODE_COMMAND
        show_advanced_options  = self.check_show_advanced_options.checkState() == Qt.Checked

        self.combo_script_file_selector.set_visible(start_mode_script_file)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
        self.label_command_help.setVisible(start_mode_command)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('ruby.version').toInt()[0]).toString())

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = []
        start_mode  = self.get_field('ruby.start_mode').toInt()[0]

        if start_mode == Constants.RUBY_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.combo_script_file.currentText()))
        elif start_mode == Constants.RUBY_START_MODE_COMMAND:
            arguments.append('-e')
            arguments.append(unicode(self.edit_command.text()))

        working_directory = unicode(self.get_field('ruby.working_directory').toString())

        return executable, arguments, environment, working_directory
