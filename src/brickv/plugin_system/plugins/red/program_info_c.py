# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

program_info_c.py: Program C/C++ Info Widget

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
from brickv.plugin_system.plugins.red.program_info import ProgramInfo
from brickv.plugin_system.plugins.red.program_utils import Constants
from brickv.plugin_system.plugins.red.ui_program_info_c import Ui_ProgramInfoC
from brickv.plugin_system.plugins.red.program_info_c_compile import ProgramInfoCCompile

class ProgramInfoC(ProgramInfo, Ui_ProgramInfoC):
    def __init__(self, context):
        ProgramInfo.__init__(self, context)

        self.setupUi(self)

        self.compile_dialog = None

        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

    # overrides ProgramInfo.update_ui_state
    def update_ui_state(self):
        show_advanced_options = self.check_show_advanced_options.isChecked()
        compile_from_source   = self.program.cast_custom_option_value('c.compile_from_source', bool, False)

        # start mode
        start_mode_api_name   = self.program.cast_custom_option_value('c.start_mode', unicode, '<unknown>')
        start_mode            = Constants.get_c_start_mode(start_mode_api_name)
        start_mode_executable = start_mode == Constants.C_START_MODE_EXECUTABLE

        self.label_start_mode.setText(Constants.c_start_mode_display_names[start_mode])
        self.label_executable_title.setVisible(start_mode_executable)
        self.label_executable.setVisible(start_mode_executable)
        self.label_working_directory_title.setVisible(show_advanced_options)
        self.label_working_directory.setVisible(show_advanced_options)
        self.label_make_options_title.setVisible(compile_from_source and show_advanced_options)
        self.label_make_options.setVisible(compile_from_source and show_advanced_options)

        # executable
        self.label_executable.setText(self.program.cast_custom_option_value('c.executable', unicode, ''))

        # compile from source
        if compile_from_source:
            self.label_compile_from_source.setText('Enabled')
        else:
            self.label_compile_from_source.setText('Disabled')

        # working directory
        self.label_working_directory.setText(self.program.working_directory)

        # make options
        self.label_make_options.setText('\n'.join(self.program.cast_custom_option_value_list('c.make_options', unicode, [])))

    # overrides ProgramInfo.close_all_dialogs
    def close_all_dialogs(self):
        if self.compile_dialog != None:
            self.compile_dialog.close()

    # overrides ProgramInfo.get_language_action
    def get_language_action(self):
        if self.program.cast_custom_option_value('c.compile_from_source', bool, False):
            return self.compile_from_source, 'Compile'
        else:
            return ProgramInfo.get_language_action(self)

    def compile_from_source(self):
        if not self.program.cast_custom_option_value('c.compile_from_source', bool, False):
            return

        self.compile_dialog = ProgramInfoCCompile(self, self.script_manager, self.program)
        self.compile_dialog.exec_()
        self.compile_dialog = None
