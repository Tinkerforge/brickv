# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtCore import pyqtProperty

from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_c import Ui_ProgramPageC

def get_gcc_versions(script_manager, callback):
    def cb_versions(result):
        if result != None:
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
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_C

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('c.start_mode', self.combo_start_mode)
        self.registerField('c.executable', self.combo_executable, 'currentText')
        self.registerField('c.working_directory', self.combo_working_directory, 'currentText')
        self.registerField('c.make_options', self, 'get_make_options')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.combo_executable_checker         = MandatoryEditableComboBoxChecker(self, self.combo_executable, self.label_executable)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self, self.combo_working_directory, self.label_working_directory)
        self.option_list_editor               = ListWidgetEditor(self.label_options,
                                                                 self.list_options,
                                                                 self.label_options_help,
                                                                 self.button_add_option,
                                                                 self.button_remove_option,
                                                                 self.button_up_option,
                                                                 self.button_down_option,
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

            self.label_compiler_available.setText('Available are {0} and {1}'.format(gcc, gpp))

        self.get_executable_versions('gcc', cb_gcc_versions)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_C_START_MODE)
        self.combo_executable.clear()
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
        if not self.combo_executable_checker.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_ui_state(self):
        start_mode            = self.get_field('c.start_mode').toInt()[0]
        start_mode_executable = start_mode == Constants.C_START_MODE_EXECUTABLE
        start_mode_make       = start_mode == Constants.C_START_MODE_MAKE
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_compiler.setVisible(start_mode_make)
        self.label_compiler_available.setVisible(start_mode_make)
        self.label_start_executable_help.setVisible(start_mode_executable)
        self.label_start_make_help.setVisible(start_mode_make)
        self.label_executable_help.setVisible(start_mode_executable)
        self.label_executable_make_help.setVisible(start_mode_make)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options and start_mode_make)

        self.option_list_editor.update_ui_state()

    @pyqtProperty(str)
    def get_make_options(self):
        return ' '.join(self.option_list_editor.get_items())

    def get_custom_options(self):
        return {}

    def get_command(self):
        executable        = unicode(self.get_field('c.executable').toString())
        arguments         = self.option_list_editor.get_items()
        environment       = []
        working_directory = unicode(self.get_field('c.working_directory').toString())

        if not executable.startswith('/'):
            executable = os.path.join('./', executable)

        return executable, arguments, environment, working_directory
