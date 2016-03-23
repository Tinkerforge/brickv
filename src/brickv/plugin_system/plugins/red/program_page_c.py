# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

program_page_c.py: Program Wizard C/C++ Page

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

from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_c import Ui_ProgramPageC
from brickv.plugin_system.plugins.red.script_manager import check_script_result
import posixpath

def get_gcc_versions(script_manager, callback):
    def cb_versions(result):
        okay, _ = check_script_result(result)

        if okay:
            try:
                versions    = result.stdout.split('\n\n')
                version_gcc = versions[0].split('\n')[0].split(' ')
                version_gpp = versions[1].split('\n')[0].split(' ')
                callback([ExecutableVersion('/usr/bin/' + version_gcc[0], version_gcc[3]),
                          ExecutableVersion('/usr/bin/' + version_gpp[0], version_gpp[3])])
                return
            except:
                pass

        # Could not get versions, we assume that some version of gcc/g++ is installed
        callback([ExecutableVersion('/usr/bin/gcc', None),
                  ExecutableVersion('/usr/bin/g++', None)])

    script_manager.execute_script('gcc_versions', cb_versions)


class ProgramPageC(ProgramPage, Ui_ProgramPageC):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.language                               = Constants.LANGUAGE_C
        self.edit_mode                              = False
        self.compile_from_source_help_new_template  = self.label_compile_from_source_help_new.text()
        self.compile_from_source_help_edit_template = self.label_compile_from_source_help_edit.text()

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('c.start_mode', self.combo_start_mode)
        self.registerField('c.executable', self.edit_executable)
        self.registerField('c.compile_from_source', self.check_compile_from_source)
        self.registerField('c.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_compile_from_source.stateChanged.connect(self.update_ui_state)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.label_spacer.setText('')

        self.edit_executable_checker          = MandatoryLineEditChecker(self,
                                                                         self.label_executable,
                                                                         self.edit_executable)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self,
                                                                           self.label_working_directory,
                                                                           self.combo_working_directory)
        self.make_option_list_editor          = ListWidgetEditor(self.label_make_options,
                                                                 self.list_make_options,
                                                                 self.label_make_options_help,
                                                                 self.button_add_make_option,
                                                                 self.button_remove_make_option,
                                                                 self.button_edit_make_option,
                                                                 self.button_up_make_option,
                                                                 self.button_down_make_option,
                                                                 '<new Make option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        def cb_gcc_versions(versions):
            if versions[0].version != None:
                gcc = '<b>{0}</b> ({1})'.format(versions[0].executable, versions[0].version)
            else:
                gcc = '<b>{0}</b>'.format(versions[0].executable)

            if versions[1].version != None:
                gpp = '<b>{0}</b> ({1})'.format(versions[1].executable, versions[1].version)
            else:
                gpp = '<b>{0}</b>'.format(versions[1].executable)

            self.label_compile_from_source_help_new.setText(self.compile_from_source_help_new_template.replace('<GCC>', gcc).replace('<G++>', gpp))
            self.label_compile_from_source_help_edit.setText(self.compile_from_source_help_edit_template.replace('<GCC>', gcc).replace('<G++>', gpp))

        self.get_executable_versions('gcc', cb_gcc_versions)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_C_START_MODE)
        self.check_compile_from_source.setChecked(False)
        self.check_show_advanced_options.setChecked(False)
        self.combo_working_directory_selector.reset()
        self.make_option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program        = self.wizard().program
            self.edit_mode = True

            # start mode
            start_mode_api_name = program.cast_custom_option_value('c.start_mode', unicode, '<unknown>')
            start_mode          = Constants.get_c_start_mode(start_mode_api_name)

            self.combo_start_mode.setCurrentIndex(start_mode)

            # executable
            self.edit_executable.setText(program.cast_custom_option_value('c.executable', unicode, ''))

            # compile from source
            self.check_compile_from_source.setChecked(program.cast_custom_option_value('c.compile_from_source', bool, False))

            # working directory
            self.combo_working_directory_selector.set_current_text(program.working_directory)

            # make options
            self.make_option_list_editor.clear()

            for make_option in program.cast_custom_option_value_list('c.make_options', unicode, []):
                self.make_option_list_editor.add_item(make_option)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        if not self.edit_executable_checker.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode            = self.get_field('c.start_mode')
        start_mode_executable = start_mode == Constants.C_START_MODE_EXECUTABLE
        compile_from_source   = self.check_compile_from_source.isChecked()
        show_advanced_options = self.check_show_advanced_options.isChecked()

        self.edit_executable.setVisible(start_mode_executable)
        self.label_executable_help.setVisible(start_mode_executable)
        self.line1.setVisible(start_mode_executable)
        self.check_compile_from_source.setVisible(start_mode_executable)
        self.label_compile_from_source_help_new.setVisible(start_mode_executable and not self.edit_mode)
        self.label_compile_from_source_help_edit.setVisible(start_mode_executable and self.edit_mode)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.make_option_list_editor.set_visible(compile_from_source and show_advanced_options)
        self.label_spacer.setVisible(not compile_from_source or not show_advanced_options)

        self.make_option_list_editor.update_ui_state()

    def get_make_options(self):
        return self.make_option_list_editor.get_items()

    def get_html_summary(self):
        start_mode          = self.get_field('c.start_mode')
        executable          = self.get_field('c.executable')
        compile_from_source = self.get_field('c.compile_from_source')
        working_directory   = self.get_field('c.working_directory')
        make_options        = ' '.join(self.make_option_list_editor.get_items())

        html = u'Start Mode: {0}<br/>'.format(Qt.escape(Constants.c_start_mode_display_names[start_mode]))

        if start_mode == Constants.C_START_MODE_EXECUTABLE:
            html += u'Executable: {0}<br/>'.format(Qt.escape(executable))

        if compile_from_source:
            html += u'Compile From Source: Enabled<br/>'
        else:
            html += u'Compile From Source: Disabled<br/>'

        html += u'Working Directory: {0}<br/>'.format(Qt.escape(working_directory))

        if compile_from_source:
            html += u'Make Options: {0}<br/>'.format(Qt.escape(make_options))

        return html

    def get_custom_options(self):
        return {
            'c.start_mode':          Constants.c_start_mode_api_names[self.get_field('c.start_mode')],
            'c.executable':          self.get_field('c.executable'),
            'c.compile_from_source': self.get_field('c.compile_from_source'),
            'c.make_options':        self.make_option_list_editor.get_items()
        }

    def get_command(self):
        executable        = self.get_field('c.executable')
        arguments         = []
        environment       = []
        working_directory = self.get_field('c.working_directory')

        if not executable.startswith('/'):
            executable = posixpath.join('./', executable)

        return executable, arguments, environment, working_directory

    def apply_program_changes(self):
        self.apply_program_custom_options_and_command_changes()
