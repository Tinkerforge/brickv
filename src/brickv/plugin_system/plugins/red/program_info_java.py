# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_info_java.py: Program Java Info Widget

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
from brickv.plugin_system.plugins.red.ui_program_info_java import Ui_ProgramInfoJava

class ProgramInfoJava(ProgramInfo, Ui_ProgramInfoJava):
    def __init__(self, context):
        ProgramInfo.__init__(self, context)

        self.setupUi(self)

        self.check_show_class_path.stateChanged.connect(self.update_ui_state)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

    # overrides ProgramInfo.update_ui_state
    def update_ui_state(self):
        show_class_path       = self.check_show_class_path.checkState() == Qt.Checked
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_class_path_title.setVisible(show_class_path)
        self.label_class_path.setVisible(show_class_path)
        self.label_working_directory_title.setVisible(show_advanced_options)
        self.label_working_directory.setVisible(show_advanced_options)
        self.label_options_title.setVisible(show_advanced_options)
        self.label_options.setVisible(show_advanced_options)

        # version
        def cb_java_versions(versions):
            for version in versions:
                if version.executable == self.program.executable:
                    self.label_version.setText(version.version)
                    return

            self.label_version.setText('<unknown>')

        self.get_executable_versions('java', cb_java_versions)

        # start mode
        start_mode_api_name   = self.program.cast_custom_option_value('java.start_mode', unicode, '<unknown>')
        start_mode            = Constants.get_java_start_mode(start_mode_api_name)
        start_mode_main_class = start_mode == Constants.JAVA_START_MODE_MAIN_CLASS
        start_mode_jar_file   = start_mode == Constants.JAVA_START_MODE_JAR_FILE

        self.label_start_mode.setText(Constants.java_start_mode_display_names[start_mode])
        self.label_main_class_title.setVisible(start_mode_main_class)
        self.label_main_class.setVisible(start_mode_main_class)
        self.label_jar_file_title.setVisible(start_mode_jar_file)
        self.label_jar_file.setVisible(start_mode_jar_file)

        # main class
        self.label_main_class.setText(self.program.cast_custom_option_value('java.main_class', unicode, '<unknown>'))

        # jar file
        self.label_jar_file.setText(self.program.cast_custom_option_value('java.jar_file', unicode, '<unknown>'))

        # class path
        self.label_class_path.setText('\n'.join(self.program.cast_custom_option_value_list('java.class_path', unicode, [])))

        # working directory
        self.label_working_directory.setText(self.program.working_directory)

        # options
        self.label_options.setText('\n'.join(self.program.cast_custom_option_value_list('java.options', unicode, [])))
