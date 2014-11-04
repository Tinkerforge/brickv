# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_javascript.py: Program Wizard JavaScript Page

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
from brickv.plugin_system.plugins.red.ui_program_page_javascript import Ui_ProgramPageJavaScript

def get_nodejs_versions(script_manager, callback):
    def cb_versions(result):
        if result != None:
            try:
                version = result.stdout.split('\n')[0]
                callback([ExecutableVersion('/usr/local/bin/node', version)])
                return
            except:
                pass

        # Could not get versions, we assume that some version of nodejs is installed
        callback([ExecutableVersion('/usr/local/bin/node', None)])

    script_manager.execute_script('nodejs_versions', cb_versions)


class ProgramPageJavaScript(ProgramPage, Ui_ProgramPageJavaScript):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_JAVASCRIPT

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('javascript.version', self.combo_version)
        self.registerField('javascript.start_mode', self.combo_start_mode)
        self.registerField('javascript.script_file', self.combo_script_file, 'currentText')
        self.registerField('javascript.command', self.edit_command)
        self.registerField('javascript.working_directory', self.combo_working_directory, 'currentText')

        self.combo_version.currentIndexChanged.connect(self.update_ui_state)
        self.combo_version.currentIndexChanged.connect(lambda: self.completeChanged.emit())
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
                                                                 '<new Node.js option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        def cb_nodejs_versions(versions):
            if versions[0].version != None:
                node_version_str = ' ' + versions[0].version
            else:
                node_version_str = ''

            self.combo_version.clear()
            self.combo_version.addItem('Client-Side (Browser)', QVariant('/bin/true'))
            self.combo_version.addItem('Server-Side (Node.js{0})'.format(node_version_str), QVariant(versions[0].executable))

            # if a program exists then this page is used in an edit wizard
            if self.wizard().program != None:
                set_current_combo_index_from_data(self.combo_version, unicode(self.wizard().program.executable))

            self.combo_version.setEnabled(True)
            self.completeChanged.emit()

        self.get_executable_versions('nodejs', cb_nodejs_versions)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_JAVASCRIPT_START_MODE)
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
        use_nodejs = self.get_field('javascript.version').toInt()[0] != 0
        start_mode = self.get_field('javascript.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if use_nodejs:
            if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE and \
               not self.combo_script_file_selector.complete:
                return False

            if start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND and \
               not self.edit_command_checker.complete:
                return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_ui_state(self):
        use_nodejs             = self.get_field('javascript.version').toInt()[0] != 0
        start_mode             = self.get_field('javascript.start_mode').toInt()[0]
        start_mode_script_file = (start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE) and use_nodejs
        start_mode_command     = (start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND) and use_nodejs
        show_advanced_options  = (self.check_show_advanced_options.checkState() == Qt.Checked) and use_nodejs

        self.label_start_mode.setVisible(use_nodejs)
        self.combo_start_mode.setVisible(use_nodejs)
        self.combo_script_file_selector.set_visible(start_mode_script_file)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
        self.label_command_help.setVisible(start_mode_command)
        self.line.setVisible(use_nodejs)
        self.check_show_advanced_options.setVisible(use_nodejs)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('javascript.version').toInt()[0]).toString())

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = [u'NODE_PATH={0}'.format(os.path.join(u'/', u'usr', u'local', u'lib', u'node_modules'))]
        start_mode  = self.get_field('javascript.start_mode').toInt()[0]

        if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.combo_script_file.currentText()))
        elif start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND:
            arguments.append('-e')
            arguments.append(unicode(self.edit_command.text()))

        working_directory = unicode(self.get_field('javascript.working_directory').toString())

        return executable, arguments, environment, working_directory
