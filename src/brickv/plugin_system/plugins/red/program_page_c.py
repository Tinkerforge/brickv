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
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_c import Ui_ProgramPageC

class ProgramPageC(ProgramPage, Ui_ProgramPageC):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_C

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('c.start_mode', self.combo_start_mode)
        self.registerField('c.file', self.combo_file, 'currentText')
        self.registerField('c.working_directory', self.combo_working_directory, 'currentText')
        self.registerField('c.make_options', self, 'get_make_options')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.combo_file_checker               = MandatoryEditableComboBoxChecker(self, self.combo_file, self.label_file)
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

        self.update_gcc_versions()

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_C_START_MODE)
        self.combo_file.clear()
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        if not self.combo_file_checker.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_gcc_versions(self):
        def done():
            self.combo_version.setEnabled(True)
            self.completeChanged.emit()

        version_str = 'Available are {0} and {1}'
        def cb_versions(result):
            if result != None:
                try:
                    versions = result.stdout.split('\n\n')
                    version_gcc = versions[0].split('\n')[0].split(' ')
                    version_gpp = versions[1].split('\n')[0].split(' ')
                    str_gcc = '<b>/usr/bin/{0}</b> ({1})'.format(version_gcc[0], version_gcc[3])
                    str_gpp = '<b>/usr/bin/{0}</b> ({1})'.format(version_gpp[0], version_gpp[3])
                    self.label_compiler_available.setText(version_str.format(str_gcc, str_gpp))
                    done()
                    return
                except:
                    pass

            # Could not get versions, we assume that some version
            # of gcc/g++ is installed
            self.label_compiler_available.setText(version_str.format('<b>/usr/bin/gcc</b>', '<b>/usr/bin/g++</b>'))
            done()

        self.wizard().script_manager.execute_script('gcc_versions', cb_versions)

    def update_ui_state(self):
        start_mode            = self.get_field('c.start_mode').toInt()[0]
        start_mode_exe        = start_mode == Constants.C_START_MODE_EXECUTABLE
        start_mode_make       = start_mode == Constants.C_START_MODE_MAKE
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_compiler.setVisible(start_mode_make)
        self.label_compiler_available.setVisible(start_mode_make)
        self.label_start_executable_help.setVisible(start_mode_exe)
        self.label_start_make_help.setVisible(start_mode_make)
        self.label_file_executable_help.setVisible(start_mode_exe)
        self.label_file_make_help.setVisible(start_mode_make)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options and start_mode_make)

        self.option_list_editor.update_ui_state()

    @pyqtProperty(str)
    def get_make_options(self):
        return ' '.join(self.option_list_editor.get_items())

    def get_command(self):
        executable = unicode(self.get_field('c.file').toString())
        if not executable.startswith('/'):
            executable = os.path.join('./', executable)
        arguments = self.option_list_editor.get_items()
        environment = []
        working_directory = unicode(self.get_field('c.working_directory').toString())

        return executable, arguments, environment, working_directory
