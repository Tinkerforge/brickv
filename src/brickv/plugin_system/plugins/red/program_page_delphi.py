# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

program_page_delphi.py: Program Wizard Delphi Page

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
from brickv.plugin_system.plugins.red.ui_program_page_delphi import Ui_ProgramPageDelphi
from brickv.plugin_system.plugins.red.script_manager import check_script_result
import posixpath

def get_fpc_versions(script_manager, callback):
    def cb_versions(result):
        okay, _ = check_script_result(result)

        if okay:
            try:
                version = result.stdout.split('\n')[0].split(' ')[-1]
                callback([ExecutableVersion('/usr/bin/fpc', version)])
                return
            except:
                pass

        # Could not get versions, we assume that some version of fpc 2.6 is installed
        callback([ExecutableVersion('/usr/bin/fpc', '2.6')])

    script_manager.execute_script('fpc_versions', cb_versions)


def get_lazbuild_versions(script_manager, callback):
    def cb_versions(result):
        okay, _ = check_script_result(result)

        if okay:
            try:
                version = result.stdout.split('\n')[0]
                callback([ExecutableVersion('/usr/bin/lazbuild', version)])
                return
            except:
                pass

        # Could not get versions, we assume that lazbuild is not installed
        callback([ExecutableVersion('/usr/bin/lazbuild', None)])

    script_manager.execute_script('lazbuild_versions', cb_versions)


class ProgramPageDelphi(ProgramPage, Ui_ProgramPageDelphi):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.language                            = Constants.LANGUAGE_DELPHI
        self.edit_mode                           = False
        self.build_system_fpcmake_help_template  = self.label_build_system_fpcmake_help.text()
        self.build_system_lazbuild_help_template = self.label_build_system_lazbuild_help.text()
        self.lazbuild_available                  = False

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('delphi.start_mode', self.combo_start_mode)
        self.registerField('delphi.executable', self.edit_executable)
        self.registerField('delphi.compile_from_source', self.check_compile_from_source)
        self.registerField('delphi.build_system', self.combo_build_system)
        self.registerField('delphi.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_compile_from_source.stateChanged.connect(self.update_ui_state)
        self.combo_build_system.currentIndexChanged.connect(self.update_ui_state)
        self.combo_build_system.currentIndexChanged.connect(self.check_build_system)
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
        self.lazbuild_option_list_editor      = ListWidgetEditor(self.label_lazbuild_options,
                                                                 self.list_lazbuild_options,
                                                                 self.label_lazbuild_options_help,
                                                                 self.button_add_lazbuild_option,
                                                                 self.button_remove_lazbuild_option,
                                                                 self.button_edit_lazbuild_option,
                                                                 self.button_up_lazbuild_option,
                                                                 self.button_down_lazbuild_option,
                                                                 '<new Lazbuild option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        def cb_fpc_versions(versions):
            if versions[0].version != None:
                fpc = '<b>{0}</b> ({1})'.format(versions[0].executable, versions[0].version)
            else:
                fpc = '<b>{0}</b>'.format(versions[0].executable)

            self.label_build_system_fpcmake_help.setText(self.build_system_fpcmake_help_template.replace('<FPC>', fpc))

        self.get_executable_versions('fpc', cb_fpc_versions)

        def cb_lazbuild_versions(versions):
            if versions[0].version != None:
                lazbuild = '<b>{0}</b> ({1})'.format(versions[0].executable, versions[0].version)
                self.lazbuild_available = True

                self.combo_build_system.setItemText(1, 'lazbuild')
            else:
                lazbuild = '<b>{0}</b>'.format(versions[0].executable)

            self.label_build_system_lazbuild_help.setText(self.build_system_lazbuild_help_template.replace('<LAZBUILD>', lazbuild))

        self.get_executable_versions('lazbuild', cb_lazbuild_versions)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_DELPHI_START_MODE)
        self.check_compile_from_source.setChecked(False)
        self.check_show_advanced_options.setChecked(False)
        self.combo_working_directory_selector.reset()
        self.make_option_list_editor.reset()
        self.lazbuild_option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program        = self.wizard().program
            self.edit_mode = True

            # start mode
            start_mode_api_name = program.cast_custom_option_value('delphi.start_mode', unicode, '<unknown>')
            start_mode          = Constants.get_delphi_start_mode(start_mode_api_name)

            self.combo_start_mode.setCurrentIndex(start_mode)

            # executable
            self.edit_executable.setText(program.cast_custom_option_value('delphi.executable', unicode, ''))

            # compile from source
            self.check_compile_from_source.setChecked(program.cast_custom_option_value('delphi.compile_from_source', bool, False))

            # build system
            build_system_api_name = program.cast_custom_option_value('delphi.build_system', unicode, '<unknown>')
            build_system          = Constants.get_delphi_build_system(build_system_api_name)

            self.combo_build_system.setCurrentIndex(build_system)

            # working directory
            self.combo_working_directory_selector.set_current_text(program.working_directory)

            # make options
            self.make_option_list_editor.clear()

            for make_option in program.cast_custom_option_value_list('delphi.make_options', unicode, []):
                self.make_option_list_editor.add_item(make_option)

            # lazbuild options
            self.lazbuild_option_list_editor.clear()

            for lazbuild_option in program.cast_custom_option_value_list('delphi.lazbuild_options', unicode, []):
                self.lazbuild_option_list_editor.add_item(lazbuild_option)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        if not self.edit_executable_checker.complete:
            return False

        if not self.lazbuild_available and \
           self.get_field('delphi.build_system') == Constants.DELPHI_BUILD_SYSTEM_LAZBUILD:
            return False

        if not self.combo_working_directory_selector.complete:
            return False

        return ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode            = self.get_field('delphi.start_mode')
        start_mode_executable = start_mode == Constants.DELPHI_START_MODE_EXECUTABLE
        compile_from_source   = self.check_compile_from_source.isChecked()
        build_system          = self.get_field('delphi.build_system')
        build_system_fpcmake  = build_system == Constants.DELPHI_BUILD_SYSTEM_FPCMAKE
        build_system_lazbuild = build_system == Constants.DELPHI_BUILD_SYSTEM_LAZBUILD
        show_advanced_options = self.check_show_advanced_options.isChecked()

        self.edit_executable.setVisible(start_mode_executable)
        self.label_executable_help.setVisible(start_mode_executable)
        self.line1.setVisible(start_mode_executable)
        self.check_compile_from_source.setVisible(start_mode_executable)
        self.label_compile_from_source_help_new.setVisible(start_mode_executable and not self.edit_mode)
        self.label_compile_from_source_help_edit.setVisible(start_mode_executable and self.edit_mode)
        self.label_build_system.setVisible(compile_from_source)
        self.combo_build_system.setVisible(compile_from_source)
        self.label_build_system_fpcmake_help.setVisible(compile_from_source and build_system_fpcmake)
        self.label_build_system_lazbuild_help.setVisible(compile_from_source and build_system_lazbuild)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.make_option_list_editor.set_visible(compile_from_source and show_advanced_options and build_system_fpcmake)
        self.lazbuild_option_list_editor.set_visible(compile_from_source and show_advanced_options and build_system_lazbuild)
        self.label_spacer.setVisible(not compile_from_source or not show_advanced_options)

        self.make_option_list_editor.update_ui_state()
        self.lazbuild_option_list_editor.update_ui_state()

    def check_build_system(self, build_system):
        if not self.lazbuild_available and \
           build_system == Constants.DELPHI_BUILD_SYSTEM_LAZBUILD:
            self.label_build_system.setStyleSheet('QLabel { color : red }')
        else:
            self.label_build_system.setStyleSheet('')

        self.completeChanged.emit()

    def get_make_options(self):
        return self.make_option_list_editor.get_items()

    def get_lazbuild_options(self):
        return self.lazbuild_option_list_editor.get_items()

    def get_html_summary(self):
        start_mode          = self.get_field('delphi.start_mode')
        executable          = self.get_field('delphi.executable')
        compile_from_source = self.get_field('delphi.compile_from_source')
        build_system        = self.get_field('delphi.build_system')
        working_directory   = self.get_field('delphi.working_directory')
        make_options        = ' '.join(self.make_option_list_editor.get_items())
        lazbuild_options    = ' '.join(self.lazbuild_option_list_editor.get_items())

        html = u'Start Mode: {0}<br/>'.format(Qt.escape(Constants.delphi_start_mode_display_names[start_mode]))

        if start_mode == Constants.DELPHI_START_MODE_EXECUTABLE:
            html += u'Executable: {0}<br/>'.format(Qt.escape(executable))

        if compile_from_source:
            html += u'Compile From Source: Enabled<br/>'
            html += u'Build System: {0}<br/>'.format(Qt.escape(Constants.delphi_build_system_display_names[build_system]))
        else:
            html += u'Compile From Source: Disabled<br/>'

        html += u'Working Directory: {0}<br/>'.format(Qt.escape(working_directory))

        if compile_from_source:
            if build_system == Constants.DELPHI_BUILD_SYSTEM_FPCMAKE:
                html += u'Make Options: {0}<br/>'.format(Qt.escape(make_options))
            elif build_system == Constants.DELPHI_BUILD_SYSTEM_LAZBUILD:
                html += u'Lazbuild Options: {0}<br/>'.format(Qt.escape(lazbuild_options))

        return html

    def get_custom_options(self):
        return {
            'delphi.start_mode':          Constants.delphi_start_mode_api_names[self.get_field('delphi.start_mode')],
            'delphi.executable':          self.get_field('delphi.executable'),
            'delphi.compile_from_source': self.get_field('delphi.compile_from_source'),
            'delphi.build_system':        Constants.delphi_build_system_api_names[self.get_field('delphi.build_system')],
            'delphi.make_options':        self.make_option_list_editor.get_items(),
            'delphi.lazbuild_options':    self.lazbuild_option_list_editor.get_items()
        }

    def get_command(self):
        executable        = self.get_field('delphi.executable')
        arguments         = []
        environment       = []
        working_directory = self.get_field('delphi.working_directory')

        if not executable.startswith('/'):
            executable = posixpath.join('./', executable)

        return executable, arguments, environment, working_directory

    def apply_program_changes(self):
        self.apply_program_custom_options_and_command_changes()
