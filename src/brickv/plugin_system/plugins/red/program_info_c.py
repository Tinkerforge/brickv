# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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
from PyQt4.QtGui import QWidget
from brickv.plugin_system.plugins.red.program_info import ProgramInfo
from brickv.plugin_system.plugins.red.program_utils import Constants
from brickv.plugin_system.plugins.red.ui_program_info_c import Ui_ProgramInfoC

class ProgramInfoC(ProgramInfo, Ui_ProgramInfoC):
    def __init__(self, context, *args, **kwargs):
        ProgramInfo.__init__(self, context, *args, **kwargs)

        self.setupUi(self)

        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

    def update_ui_state(self):
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked
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
        self.label_options_title.setVisible(compile_from_source and show_advanced_options)
        self.label_options.setVisible(compile_from_source and show_advanced_options)

        # executable
        self.label_executable.setText(self.program.cast_custom_option_value('c.executable', unicode, ''))

        # compile from source
        if compile_from_source:
            self.label_compile_from_source.setText('Enabled')
        else:
            self.label_compile_from_source.setText('Disabled')

        # working directory
        self.label_working_directory.setText(unicode(self.program.working_directory))

        # options
        self.label_options.setText('\n'.join(self.program.cast_custom_option_value_list('c.options', unicode, [])))
