# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_javascript import Ui_ProgramPageJavaScript
from brickv.utils import get_main_window

def get_nodejs_versions(script_manager, callback):
    def cb_versions(result):
        if result != None:
            try:
                version = result.stdout.split('\n')[0].replace('v', '')
                callback([ExecutableVersion('/usr/local/bin/node', version)])
                return
            except:
                pass

        # Could not get versions, we assume that some version of nodejs is installed
        callback([ExecutableVersion('/usr/local/bin/node', None)])

    script_manager.execute_script('nodejs_versions', cb_versions)


class ProgramPageJavaScript(ProgramPage, Ui_ProgramPageJavaScript):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_JAVASCRIPT

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('javascript.flavor', self.combo_flavor)
        self.registerField('javascript.start_mode', self.combo_start_mode)
        self.registerField('javascript.script_file', self.combo_script_file, 'currentText')
        self.registerField('javascript.command', self.edit_command)
        self.registerField('javascript.working_directory', self.combo_working_directory, 'currentText')

        self.combo_flavor.currentIndexChanged.connect(self.update_ui_state)
        self.combo_flavor.currentIndexChanged.connect(self.completeChanged.emit)
        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.label_spacer.setText('')

        self.combo_script_file_selector       = MandatoryTypedFileSelector(self,
                                                                           self.label_script_file,
                                                                           self.combo_script_file,
                                                                           self.label_script_file_type,
                                                                           self.combo_script_file_type,
                                                                           self.label_script_file_help)
        self.edit_command_checker             = MandatoryLineEditChecker(self,
                                                                         self.label_command,
                                                                         self.edit_command)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self,
                                                                           self.label_working_directory,
                                                                           self.combo_working_directory)
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

            self.combo_flavor.clear()
            self.combo_flavor.addItem('Client-Side (Browser)', QVariant('/bin/false'))
            self.combo_flavor.addItem('Server-Side (Node.js{0})'.format(node_version_str), QVariant(versions[0].executable))

            # if a program exists then this page is used in an edit wizard
            if self.wizard().program != None:
                program         = self.wizard().program
                flavor_api_name = program.cast_custom_option_value('javascript.flavor', unicode, '<unknown>')
                flavor          = Constants.get_javascript_flavor(flavor_api_name)

                if flavor == Constants.JAVASCRIPT_FLAVOR_BROWSER:
                    executable = '/bin/false'
                else:
                    executable = unicode(program.executable)

                set_current_combo_index_from_data(self.combo_flavor, executable)

            self.combo_flavor.setEnabled(True)
            self.completeChanged.emit()

        self.get_executable_versions('nodejs', cb_nodejs_versions)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_JAVASCRIPT_START_MODE)
        self.combo_script_file_selector.reset()
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        program = self.wizard().program

        if program != None:
            # start mode
            start_mode_api_name = program.cast_custom_option_value('javascript.start_mode', unicode, '<unknown>')
            start_mode          = Constants.get_javascript_start_mode(start_mode_api_name)

            self.combo_start_mode.setCurrentIndex(start_mode)

            # script file
            self.combo_script_file_selector.set_current_text(program.cast_custom_option_value('javascript.script_file', unicode, ''))

            # command
            self.edit_command.setText(program.cast_custom_option_value('javascript.command', unicode, ''))

            # working directory
            self.combo_working_directory_selector.set_current_text(unicode(program.working_directory))

            # options
            self.option_list_editor.clear()

            for option in program.cast_custom_option_value_list('javascript.options', unicode, []):
                self.option_list_editor.add_item(option)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        flavor     = self.get_field('javascript.flavor').toInt()[0] != 0
        executable = self.get_executable()
        start_mode = self.get_field('javascript.start_mode').toInt()[0]

        if flavor == Constants.JAVASCRIPT_FLAVOR_NODEJS:
            if len(executable) == 0:
                return False

            if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE and \
               not self.combo_script_file_selector.complete:
                return False

            if start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND and \
               not self.edit_command_checker.complete:
                return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        flavor                 = self.get_field('javascript.flavor').toInt()[0]
        flavor_browser         = flavor == Constants.JAVASCRIPT_FLAVOR_BROWSER
        flavor_nodejs          = flavor == Constants.JAVASCRIPT_FLAVOR_NODEJS
        start_mode             = self.get_field('javascript.start_mode').toInt()[0]
        start_mode_script_file = start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE
        start_mode_command     = start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND
        show_advanced_options  = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_start_mode.setVisible(flavor_nodejs)
        self.combo_start_mode.setVisible(flavor_nodejs)
        self.combo_script_file_selector.set_visible(flavor_nodejs and start_mode_script_file)
        self.label_command.setVisible(flavor_nodejs and start_mode_command)
        self.edit_command.setVisible(flavor_nodejs and start_mode_command)
        self.label_command_help.setVisible(flavor_nodejs and start_mode_command)
        self.line.setVisible(flavor_nodejs)
        self.check_show_advanced_options.setVisible(flavor_nodejs)
        self.combo_working_directory_selector.set_visible(flavor_nodejs and show_advanced_options)
        self.option_list_editor.set_visible(flavor_nodejs and show_advanced_options)
        self.label_spacer.setVisible(flavor_browser or not show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_flavor.itemData(self.get_field('javascript.flavor').toInt()[0]).toString())

    def get_html_summary(self):
        flavor            = self.get_field('javascript.flavor').toInt()[0]
        start_mode        = self.get_field('javascript.start_mode').toInt()[0]
        script_file       = self.get_field('javascript.script_file').toString()
        command           = self.get_field('javascript.command').toString()
        working_directory = self.get_field('javascript.working_directory').toString()
        options           = ' '.join(self.option_list_editor.get_items())

        html = u'JavaScript Flavor: {0}<br/>'.format(Qt.escape(self.combo_flavor.itemText(flavor)))

        if flavor == Constants.JAVASCRIPT_FLAVOR_NODEJS:
            html += u'Start Mode: {0}<br/>'.format(Qt.escape(Constants.javascript_start_mode_display_names[start_mode]))

            if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE:
                html += u'Script File: {0}<br/>'.format(Qt.escape(script_file))
            elif start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND:
                html += u'Command: {0}<br/>'.format(Qt.escape(command))

            html += u'Working Directory: {0}<br/>'.format(Qt.escape(working_directory))
            html += u'Node.js Options: {0}<br/>'.format(Qt.escape(options))

        return html

    def get_custom_options(self):
        return {
            'javascript.flavor':      Constants.javascript_flavor_api_names[self.get_field('javascript.flavor').toInt()[0]],
            'javascript.start_mode':  Constants.javascript_start_mode_api_names[self.get_field('javascript.start_mode').toInt()[0]],
            'javascript.script_file': unicode(self.get_field('javascript.script_file').toString()),
            'javascript.command':     unicode(self.get_field('javascript.command').toString()),
            'javascript.options':     self.option_list_editor.get_items()
        }

    def get_command(self):
        flavor = self.get_field('javascript.flavor').toInt()[0]

        if flavor == Constants.JAVASCRIPT_FLAVOR_BROWSER:
            return None

        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = ['NODE_PATH=/usr/local/lib/node_modules']
        start_mode  = self.get_field('javascript.start_mode').toInt()[0]

        if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.get_field('javascript.script_file').toString()))
        elif start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND:
            arguments.append('-e')
            arguments.append(unicode(self.get_field('javascript.command').toString()))

        working_directory = unicode(self.get_field('javascript.working_directory').toString())

        return executable, arguments, environment, working_directory

    def apply_program_changes(self):
        if not self.apply_program_custom_options_and_command_changes():
            return

        # stop scheduler if switching to browser flavor
        if self.get_field('javascript.flavor').toInt()[0] == Constants.JAVASCRIPT_FLAVOR_BROWSER:
            try:
                program.set_schedule(REDProgram.START_MODE_NEVER, False, 0, '') # FIXME: async_call
            except REDError as e:
                QMessageBox.critical(get_main_window(), 'Edit Program Error',
                                     u'Could not update schedule of program [{0}]:\n\n{1}'
                                     .format(program.cast_custom_option_value('name', unicode, '<unknown>')))
